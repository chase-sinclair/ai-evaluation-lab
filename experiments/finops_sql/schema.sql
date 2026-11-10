CREATE TABLE provider (
    id INTEGER,
    name VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE account (
    id INTEGER,
    provider_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (provider_id) REFERENCES provider(id)
);

CREATE TABLE project (
    id INTEGER,
    account_id INTEGER,
    name VARCHAR,
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES account(id)
);

CREATE TABLE region (
    id INTEGER,
    name VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE service_class (
    id INTEGER,
    name VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE service (
    id INTEGER,
    class_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (class_id) REFERENCES service_class(id)
);

CREATE TABLE sku (
    id INTEGER,
    service_id INTEGER,
    unit VARCHAR,
    PRIMARY KEY (id),
    FOREIGN KEY (service_id) REFERENCES service(id)
);

CREATE TABLE resource (
    id INTEGER,
    project_id INTEGER,
    sku_id INTEGER,
    region_id INTEGER,
    metadata JSON,
    PRIMARY KEY (id),
    FOREIGN KEY (project_id) REFERENCES project(id),
    FOREIGN KEY (sku_id) REFERENCES sku(id),
    FOREIGN KEY (region_id) REFERENCES region(id)
);

CREATE TABLE cost_center (
    id INTEGER,
    name VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE team (
    id INTEGER,
    center_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (center_id) REFERENCES cost_center(id)
);

CREATE TABLE resource_owner (
    resource_id INTEGER,
    team_id INTEGER,
    first_day DATE,
    end_day DATE,
    share DECIMAL(18,6),
    PRIMARY KEY (resource_id, team_id, first_day),
    FOREIGN KEY (resource_id) REFERENCES resource(id),
    FOREIGN KEY (team_id) REFERENCES team(id)
);

CREATE TABLE resource_tag (
    resource_id INTEGER,
    tag_key VARCHAR,
    tag_value VARCHAR,
    first_day DATE,
    end_day DATE,
    PRIMARY KEY (resource_id, tag_key, first_day),
    FOREIGN KEY (resource_id) REFERENCES resource(id)
);

CREATE TABLE fiscal_period (
    id INTEGER,
    first_day DATE,
    end_day DATE,
    PRIMARY KEY (id)
);

CREATE TABLE invoice (
    id INTEGER,
    account_id INTEGER,
    posting_month INTEGER,
    control DECIMAL(18,6),
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES account(id)
);

CREATE TABLE usage_day (
    id INTEGER,
    resource_id INTEGER,
    day DATE,
    units INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (resource_id) REFERENCES resource(id)
);

CREATE TABLE commitment (
    id INTEGER,
    sku_id INTEGER,
    account_id INTEGER,
    first_day DATE,
    end_day DATE,
    purchase DECIMAL(18,6),
    monthly DECIMAL(18,6),
    PRIMARY KEY (id),
    FOREIGN KEY (sku_id) REFERENCES sku(id),
    FOREIGN KEY (account_id) REFERENCES account(id)
);

CREATE TABLE charge_revision (
    charge_id INTEGER,
    revision INTEGER,
    export_id INTEGER,
    arrived DATE,
    invoice_id INTEGER,
    day DATE,
    resource_id INTEGER,
    meter_id INTEGER,
    sku_id INTEGER,
    category VARCHAR,
    origin_id INTEGER,
    pool VARCHAR,
    contract_id INTEGER,
    billed DECIMAL(18,6),
    effective DECIMAL(18,6),
    list_cost DECIMAL(18,6),
    contracted DECIMAL(18,6),
    memo VARCHAR,
    PRIMARY KEY (export_id),
    FOREIGN KEY (invoice_id) REFERENCES invoice(id),
    FOREIGN KEY (resource_id) REFERENCES resource(id),
    FOREIGN KEY (meter_id) REFERENCES usage_day(id),
    FOREIGN KEY (sku_id) REFERENCES sku(id),
    FOREIGN KEY (contract_id) REFERENCES commitment(id)
);

CREATE TABLE price_schedule (
    sku_id INTEGER,
    region_id INTEGER,
    first_day DATE,
    end_day DATE,
    list_rate DECIMAL(18,6),
    contract_rate DECIMAL(18,6),
    PRIMARY KEY (sku_id, region_id, first_day),
    FOREIGN KEY (sku_id) REFERENCES sku(id),
    FOREIGN KEY (region_id) REFERENCES region(id)
);

CREATE TABLE commitment_application (
    contract_id INTEGER,
    charge_id INTEGER,
    covered INTEGER,
    applied DECIMAL(18,6),
    PRIMARY KEY (contract_id, charge_id),
    FOREIGN KEY (contract_id) REFERENCES commitment(id)
);

CREATE TABLE shared_split (
    month_id INTEGER,
    pool VARCHAR,
    center_id INTEGER,
    weight DECIMAL(18,6),
    PRIMARY KEY (month_id, pool, center_id),
    FOREIGN KEY (center_id) REFERENCES cost_center(id)
);

CREATE TABLE monthly_budget (
    period_id INTEGER,
    center_id INTEGER,
    budget DECIMAL(18,6),
    PRIMARY KEY (period_id, center_id),
    FOREIGN KEY (period_id) REFERENCES fiscal_period(id),
    FOREIGN KEY (center_id) REFERENCES cost_center(id)
);

CREATE TABLE output_day (
    project_id INTEGER,
    day DATE,
    transactions INTEGER,
    PRIMARY KEY (project_id, day),
    FOREIGN KEY (project_id) REFERENCES project(id)
);
