CREATE TABLE IF NOT EXISTS t_building_codes (
    code      VARCHAR(10)
    , name    VARCHAR(255)
    , ref     INT
)
;

COPY t_building_codes FROM '/Users/mdelhey/rice-scrape/data/codes.csv' DELIMITER ',' CSV
;
