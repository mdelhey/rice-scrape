library(ggplot2)
library(plyr)
library(dplyr)
library(ggvis)
library(RPostgreSQL)

dbuser <- "mdelhey"
dbname <- "ricedb"
dbhost <- "localhost"

project_dir <- "/Users/mdelhey/rice-scrape/"
setwd(project_dir)

# Query
rdb.con <- dbConnect(PostgreSQL(), host = dbhost, user = dbuser, dbname = dbname)
tbl <- dbGetQuery(rdb.con, "select * from t_courses")
tbl <- tbl_df(tbl)

# Department
tbl.dp <-
    tbl %>%
    filter(as.numeric(course_number) >= 300) %>%
    filter(course_level == "Undergrad") %>%
    group_by(department) %>%
    summarize(tot_enr = sum(enrolled),
              nclasses = length(department),
              class_size = tot_enr / nclasses) %>%
    arrange(-tot_enr) %>%
    filter(tot_enr > 100)

# ggvis
department_tooltip <- function(point) {
    if(is.null(point)) return(NULL)
    row <- tbl.dp[tbl.dp$department == point$department, ]
    sprintf("<b>%s</b> <br /> Undergraduate Enrollment: %i <br /> Number of Classes: %i <br /> Average Class Size: %.1f", row$department, row$tot_enr, row$nclasses, row$class_size)
}

ggvis(tbl.dp, ~tot_enr, ~department) %>%
    layer_points() %>%
    add_axis("x", title = "undergraduate enrollment") %>%
    add_axis("y", title = "department", title_offset = 55) 

ggvis(arrange(tbl.dp, -class_size), ~class_size, ~department) %>%
    layer_points() %>%
    add_axis("x", title = "average class size") %>%
    add_axis("y", title = "department", title_offset = 55) 
