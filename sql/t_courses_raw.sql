drop table if exists t_courses_raw;
create table t_courses_raw (    
    crn	     	varchar(10)
    , course	varchar(255)
    , title	varchar(255)
    , faculty   varchar(255)
    , meeting   varchar(255)
    , credits   varchar(255)
    , enrolled  varchar(255)
)
;

copy
  t_courses_raw 
from
  '/Users/mdelhey/rice-scrape/data/courses.csv' 
with
  CSV HEADER DELIMITER ','
;
