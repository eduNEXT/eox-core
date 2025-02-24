PREDEFINED_QUERIES = {
    "Usuarios total": """
        SELECT COUNT(*) FROM auth_user as au;
    """,
    "Usuarios activos mes anterior": """
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
    """,
    "Usuarios activos 7 dias": """
        SELECT COUNT(DISTINCT cs.student_id)
        FROM courseware_studentmodule AS cs
        WHERE cs.modified >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
    """,
    "Cantidad de cursos creados": """
        SELECT COUNT(*) FROM course_overviews_courseoverview as coc;
    """,
    "Cursos activos": """
        SELECT COUNT(*)
        FROM course_overviews_courseoverview as coc
        WHERE coc.start <= NOW() AND (coc.end >= NOW() OR coc.end IS NULL);
    """,
    "Cursos con certificado activo": """
        SELECT COUNT(DISTINCT coc.id)
        FROM course_overviews_courseoverview AS coc
        JOIN certificates_generatedcertificate AS cg
        ON coc.id = cg.course_id;
    """,
    "Inscripciones mes anterior": """
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
    """,
    "Inscripciones 7 dias": """
        SELECT COUNT(DISTINCT sc.id)
        FROM student_courseenrollment AS sc
        WHERE sc.created >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
    """,
    "Certificados generados": """
        SELECT COUNT(*) FROM certificates_generatedcertificate as cg;
    """,
}
