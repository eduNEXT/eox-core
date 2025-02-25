"""
This module contains SQL queries to retrieve platform-related metrics.

These queries are used to extract information about user activity, course 
engagement, and certificate issuance. The data retrieval is conditioned on 
the feature being enabled and the necessary authentication credentials 
being set.
"""

# This query counts the total number of users in the platform.
TOTAL_USERS_QUERY = """
SELECT
  COUNT(*)
FROM
  auth_user as au;
"""
# This query counts the number of unique active users in the last month.
# A user is considered active if they have modified a student module within the last month.
ACTIVE_USERS_LAST_MONTH_QUERY = """
SELECT
  YEAR(cs.modified) AS 'Year',
  MONTH(cs.modified) AS 'Month',
    COUNT(DISTINCT cs.student_id) AS 'Active Users'
FROM
    courseware_studentmodule AS cs
WHERE
    cs.modified >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
    AND cs.modified < DATE_FORMAT(CURDATE(), '%Y-%m-01')
GROUP BY
    YEAR(cs.modified), MONTH(cs.modified);
"""
# This query counts the number of unique active users in the last 7 days.
# A user is considered active if they have modified a student module within the last 7 days.
ACTIVE_USERS_LAST_7_DAYS_QUERY = """
SELECT
  COUNT(DISTINCT cs.student_id)
FROM
  courseware_studentmodule AS cs
WHERE
  cs.modified >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
"""
# This query counts the total number of courses created on the platform.
TOTAL_COURSES_CREATED_QUERY = """
SELECT
  COUNT(*)
FROM
  course_overviews_courseoverview as coc;
"""
# This query counts the number of CourseOverviews objects that started before
# now and have not yet ended
ACTIVE_COURSES_COUNT_QUERY = """
SELECT
  COUNT(*)
FROM
  course_overviews_courseoverview as coc
WHERE
  coc.start <= NOW()
  AND (
    coc.end >= NOW()
    OR coc.end IS NULL
  );
"""
# This query counts the number of courses that have at least one issued certificate.
COURSES_WITH_ACTIVE_CERTIFICATES_QUERY = """
SELECT
  COUNT(DISTINCT coc.id)
FROM
  course_overviews_courseoverview AS coc
JOIN
  certificates_generatedcertificate AS cg
ON
  coc.id = cg.course_id;
"""
# This query counts the number of new enrollments in the last month.
ENROLLMENTS_LAST_MONTH_QUERY = """
SELECT
  YEAR(sc.created) AS 'Year',
  MONTH(sc.created) AS 'Month',
  COUNT(DISTINCT sc.id) AS 'Enrollments'
FROM
  student_courseenrollment AS sc
WHERE
  sc.created >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
  AND sc.created < DATE_FORMAT(CURDATE(), '%Y-%m-01')
GROUP BY
  YEAR(sc.created), MONTH(sc.created);
"""
# This query counts the number of new enrollments in the last 7 days.
ENROLLMENTS_LAST_7_DAYS_QUERY = """
SELECT
  COUNT(DISTINCT sc.id)
FROM
  student_courseenrollment AS sc
WHERE
  sc.created >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
"""
CERTIFICATES_ISSUED_QUERY = """
SELECT
  COUNT(*)
FROM
  certificates_generatedcertificate as cg;
"""
# This query counts the total number of certificates issued on the platform.
PREDEFINED_QUERIES = {
    "Total Users": TOTAL_USERS_QUERY,
    "Active Users Last Month": ACTIVE_USERS_LAST_MONTH_QUERY,
    "Active users in the last 7 days": ACTIVE_USERS_LAST_7_DAYS_QUERY,
    "Total Courses Created": TOTAL_COURSES_CREATED_QUERY,
    "Active Courses Count": ACTIVE_COURSES_COUNT_QUERY,
    "Courses With Active Certificates": COURSES_WITH_ACTIVE_CERTIFICATES_QUERY,
    "Enrollments Last Month": ENROLLMENTS_LAST_MONTH_QUERY,
    "Enrollments Last 7 Days": ENROLLMENTS_LAST_7_DAYS_QUERY,
    "Certificates Issued": CERTIFICATES_ISSUED_QUERY,   
}
