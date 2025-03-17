import warnings

warnings.filterwarnings('ignore')
# import re


class paidDataQueries:

  def __init__(self, start_date, end_date):
    self.start_date = start_date
    self.end_date = end_date

  def paidDataByPhone(self, phone):
    formatted_phones = ','.join(
        [re.sub(r'\D', '', str(p))[-8:] for p in phone])
    query = f'''
        SELECT     RIGHT(REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(mobile_no1, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ), 8) AS paid_list
        FROM billing_details
        INNER JOIN (SELECT email_id AS email FROM order_details
                    WHERE program_type = 0 AND DATE(date) BETWEEN DATE('{self.start_date}') 
                    AND DATE('{self.end_date}')) od
        ON od.email = email_id
        WHERE RIGHT(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(mobile_no1, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ),
                    8) IN ({formatted_phones})

        '''
    return query

  def paidDataByEmail(self, email):
    email_list = ','.join([f"'{emails}'" for emails in email])
    query = f"""
                SELECT DISTINCT email_id AS paid_email FROM order_details
                WHERE email_id IN ({email_list})  
                AND DATE(date) BETWEEN DATE('{self.start_date}') 
               AND DATE('{self.end_date}') AND program_type = 0

               """
    return query


class summaryQueries:

  def __init__(self, start_date, end_date):
    self.start_date = start_date
    self.end_date = end_date

  def gutDetoxAssignedLeadSummary(self):
    query = f'''
        SELECT 
        assignedTo AS Name,
        SUM(CASE WHEN leadType = 'New' THEN 1 ELSE 0 END) AS `New`,
        SUM(CASE WHEN leadType = 'OL' THEN 1 ELSE 0 END) AS `OL`,
        SUM(CASE WHEN leadType = 'OC' THEN 1 ELSE 0 END) AS `OC`,
        COUNT(*) AS `Total`
        FROM (SELECT * FROM gutsociallead gl
        WHERE DATE(gl.created) BETWEEN ('{self.start_date}') AND ('{self.end_date}')
        GROUP BY RIGHT(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(gl.leadNumber, '(', ''),
                        ')',
                        ''
                      ),
                      ' ',
                      ''
                    ),
                    '-',
                    ''
                  ),
                  '+',
                  ''
                ),
                8
              )) AS sheet
        GROUP BY assignedTo      


        '''
    return query

  def socialMediaAssignedLeadsSummary(self):
    query = f'''
            SELECT 
            sl.assignedTo AS `Name`,
            SUM(CASE WHEN (sl.leadType = 'New') THEN 1 ELSE 0 END) AS
            totalNew,
            SUM(CASE WHEN (sl.leadType = 'New' AND sl.source_type = 'SMO') THEN 1 ELSE 0 END) AS
            newSMO,
            SUM(CASE WHEN (sl.leadType = 'New' AND sl.source_type = 'SME') THEN 1 ELSE 0 END) AS newSME,
            SUM(CASE WHEN (sl.leadType = 'OL') THEN 1 ELSE 0 END) AS
            totalOl,
            SUM(CASE WHEN (sl.leadType = 'OL' AND sl.source_type = 'SMO') THEN 1 ELSE 0 END) 
            AS olSMO,
            SUM(CASE WHEN (sl.leadType = 'OL' AND sl.source_type = 'SME') THEN 1 ELSE 0 END) 
            AS olSME
            FROM sociallead sl
            WHERE DATE(sl.created) BETWEEN DATE("{self.start_date}") AND DATE("{self.end_date}")
            GROUP BY sl.assignedTo
        '''
    return query

  def tailendSummaryQuery(self):
    query = f"""
                SELECT mentor AS Mentor, COUNT(user_id) AS Total,
                SUM(CASE WHEN (pitched_program IS NOT NULL OR REPLACE(pitched_program, " ", "") NOT IN ("")) 
                THEN 1 ELSE 0 END) AS Pitched,
                SUM(CASE WHEN (pitched_program IS NULL OR REPLACE(pitched_program, " ", "") IN (""))
                THEN 1 ELSE 0 END) AS `Not Pitched`
                FROM
                (SELECT
                    rg.id AS user_id,
                    CONCAT(rg.first_name, ' ', rg.last_name) AS full_name,
                    rg.first_name,
                    rg.email_id,
                    (
                    SELECT
                        order_id
                    FROM
                        order_details
                    WHERE
                        program_status = 1 AND userid = rg.id
                    ORDER BY
                        order_id
                    DESC
                LIMIT 1
                ) AS order_id, rg.user_status, rg.my_wallet,CONCAT("''", (
                    SELECT
                        mobile_no1
                    FROM
                        billing_details
                    WHERE
                        user_id = rg.id
                    ORDER BY
                        billing_id
                    DESC
                LIMIT 1
                )) AS phone,(
                    SELECT
                        COUNT(order_id)
                    FROM
                        order_details
                    WHERE
                        order_type = 'Renewal' AND userid = rg.id
                ) AS renewal_count,
                (
                    (
                    SELECT
                        SUM(program_session)
                    FROM
                        order_details
                    WHERE
                        userid = rg.id
                    GROUP BY
                        userid
                ) -(
                    SELECT
                        COUNT(DISTINCT(SESSION))
                    FROM
                        diet_session_log
                    WHERE
                        user_id = rg.id AND is_deleted = 0 AND diet_status = '4'
                )
                ) AS pending_sessions,
                (
                    SELECT
                        COUNT(order_id)
                    FROM
                        order_details
                    WHERE
                        userid = rg.id
                ) AS progrme_number,
                (
                    SELECT
                        first_name
                    FROM
                        admin_user
                    WHERE
                        admin_id = rg.mentor_id AND admin_id NOT IN (196, 0 '')
                ) AS mentor,
                (
                    SELECT
                        userid
                    FROM
                        order_details
                    WHERE
                        userid = rg.id AND program_type = 1 AND userid NOT IN(
                        SELECT
                            userid
                        FROM
                            order_details
                        WHERE
                            program_type = 0
                    )
                ORDER BY
                    order_id
                DESC
                LIMIT 1
                ) AS cleanse_purchase,(SELECT suggested_program FROM bn_suggested_program WHERE user_id = rg.id 
                AND DATE(added_date) >= DATE('{self.start_date}') AND DATE(added_date) <= DATE('{self.end_date}')  
                ORDER BY added_date DESC LIMIT 1) as pitched_program,
                (SELECT user_id FROM bn_suggested_program WHERE user_id = rg.id AND DATE(added_date) >= DATE('{self.start_date}')
                 AND DATE(added_date) <= DATE('{self.end_date}')             
                ORDER BY added_date DESC LIMIT 1) as pitched_id,
                (SELECT user_id FROM bn_suggested_program WHERE user_id = rg.id 
                AND DATE(added_date) >= DATE('{self.start_date}') AND DATE(added_date) <= DATE('{self.end_date}') AND lead_status like '%Pitch1%' 
                ORDER BY added_date DESC LIMIT 1) as first_pitched 
                FROM
                    registries rg
                WHERE
                    rg.user_status IN(
                        'active',
                        'dormant',
                        'onhold',
                        'premaintenance',
                        'maintenance',
                        'notstarted',
                        'not started'
                    ) AND(
                        (
                        SELECT
                            SUM(program_session)
                        FROM
                            order_details
                        WHERE
                            userid = rg.id
                        GROUP BY
                            userid
                    ) -(
                    SELECT
                        COUNT(DISTINCT(SESSION))
                    FROM
                        diet_session_log
                    WHERE
                        user_id = rg.id AND is_deleted = 0 AND diet_status = '4'
                )
                    ) <= 3 AND rg.id NOT IN(
                    SELECT
                        userid
                    FROM
                        order_details
                    WHERE
                        program_status IN(4)
                ) ) AS datas
                GROUP BY datas.mentor;

                """
    return query

  def leadWithoutRefSummaryQuery(self):
    query = f""" 
                       SELECT
                          allData.assign_to AS Mentor,
                          allData.Total,
                          COALESCE(paid.`Un Paid`, 0) AS `Un Paid`,
                          (
                            allData.Total - COALESCE(paid.`Un Paid`, 0)
                          ) AS `Paid`
                        FROM
                          (
                            -- Subquery to get Total Leads assigned
                            SELECT
                              assign_to,
                              COALESCE(
                                COUNT(DISTINCT email),
                                0
                              ) AS Total
                            FROM
                              (
                                SELECT
                                  lm.fname,
                                  lm.email,
                                  REPLACE(
                                    REPLACE(
                                      REPLACE(
                                        REPLACE(
                                          REPLACE(lm.phone, '(', ''),
                                          ')',
                                          ''
                                        ),
                                        ' ',
                                        ''
                                      ),
                                      '-',
                                      ''
                                    ),
                                    '+',
                                    ''
                                  ) AS phone,
                                  la.assign_to,
                                  DATE(la.assign_date) AS assign_date
                                FROM
                                  lead_management lm
                                  LEFT JOIN lead_management lm1 ON (
                                    lm1.email = lm.email
                                    AND lm.id < lm1.id
                                  )
                                  LEFT JOIN lead_action la ON la.email = lm.email
                                  LEFT JOIN lead_action la2 ON (
                                    la.email = la2.email
                                    AND la.id < la2.id
                                  )
                                WHERE
                                  lm1.id IS NULL
                                  AND la2.id IS NULL
                                  AND (
                                    lm.enquiry_from NOT LIKE '%Referral%'
                                    OR lm.enquiry_from IS NULL
                                  )
                                  AND la.assign_to NOT IN (
                                    'Client', 'Client Services', 'Nikita',
                                    'NikitaK', 'Select', 'Vrushali',
                                    'Saloni', 'Nidhi', 'Chanchal', 'Khyati',
                                    'Shubhangi'
                                  )
                                  AND DATE(la.assign_date) >= DATE('2024-09-01')
                                GROUP BY
                                  REPLACE(
                                    REPLACE(
                                      REPLACE(
                                        REPLACE(
                                          REPLACE(lm.phone, '(', ''),
                                          ')',
                                          ''
                                        ),
                                        ' ',
                                        ''
                                      ),
                                      '-',
                                      ''
                                    ),
                                    '+',
                                    ''
                                  )
                              ) AS ash
                            GROUP BY
                              assign_to
                          ) AS allData
                          LEFT JOIN (
                            -- Subquery to get Unpaid Leads
                            SELECT
                              assign_to,
                              COALESCE(
                                COUNT(DISTINCT email),
                                0
                              ) AS `Un Paid`
                            FROM
                              (
                                SELECT
                                  lm.fname,
                                  lm.email,
                                  REPLACE(
                                    REPLACE(
                                      REPLACE(
                                        REPLACE(
                                          REPLACE(lm.phone, '(', ''),
                                          ')',
                                          ''
                                        ),
                                        ' ',
                                        ''
                                      ),
                                      '-',
                                      ''
                                    ),
                                    '+',
                                    ''
                                  ) AS phone,
                                  la.assign_to,
                                  DATE(la.assign_date) AS assign_date
                                FROM
                                  lead_management lm
                                  LEFT JOIN lead_management lm1 ON (
                                    lm1.email = lm.email
                                    AND lm.id < lm1.id
                                  )
                                  LEFT JOIN lead_action la ON la.email = lm.email
                                  LEFT JOIN lead_action la2 ON (
                                    la.email = la2.email
                                    AND la.id < la2.id
                                  )
                                WHERE
                                  lm1.id IS NULL
                                  AND la2.id IS NULL
                                  AND (
                                    lm.enquiry_from NOT LIKE '%Referral%'
                                    OR lm.enquiry_from IS NULL
                                  )
                                  AND la.assign_to NOT IN (
                                    'Client', 'Client Services', 'Nikita',
                                    'NikitaK', 'Select', 'Vrushali',
                                    'Saloni', 'Nidhi', 'Chanchal', 'Khyati',
                                    'Shubhangi'
                                  )
                                  AND DATE(la.assign_date) >= DATE('2024-09-01')

                                GROUP BY
                                  REPLACE(
                                    REPLACE(
                                      REPLACE(
                                        REPLACE(
                                          REPLACE(lm.phone, '(', ''),
                                          ')',
                                          ''
                                        ),
                                        ' ',
                                        ''
                                      ),
                                      '-',
                                      ''
                                    ),
                                    '+',
                                    ''
                                  )
                              ) AS ash
                              LEFT JOIN (
                                SELECT
                                  email_id
                                FROM
                                  order_details
                              ) od ON od.email_id = email
                              LEFT JOIN (
                                SELECT
                                  mobile_no1
                                FROM
                                  billing_details
                              ) bd ON RIGHT(
                                REPLACE(
                                  REPLACE(
                                    REPLACE(
                                      REPLACE(
                                        REPLACE(bd.mobile_no1, '(', ''),
                                        ')',
                                        ''
                                      ),
                                      ' ',
                                      ''
                                    ),
                                    '-',
                                    ''
                                  ),
                                  '+',
                                  ''
                                ),
                                8
                              ) = RIGHT(phone, 8)
                            WHERE
                              (
                                od.email_id IS NULL
                                AND bd.mobile_no1 IS NULL
                              )
                            GROUP BY
                              assign_to
  ) AS paid ON allData.assign_to = paid.assign_to

                """
    return query

  def activeNoAdvPurchaseSummaryQuery(self):
    query = f"""
            SELECT mentor_name AS Mentor, 
            COUNT(mentor_name) AS Total,
            SUM(CASE WHEN sugg_program_name NOT IN ("") OR sugg_program_name IS NOT NULL 
            THEN 1 ELSE 0 END) AS Pitched,
            SUM(CASE WHEN (sugg_program_name IN ("") OR sugg_program_name IS NULL) 
            THEN 1 ELSE 0 END) AS `Un-Pitched`
            FROM (SELECT
                CONCAT(a.first_name, ' ', a.last_name) AS Name,
                a.id AS client_id,
                (SELECT concat("''", mobile_no1) FROM billing_details WHERE email_id=a.email_id LIMIT 1) as mobile,
                a.email_id,
                a.my_wallet,
                a.old_wallet,
                (
                SELECT
                    suggested_program
                FROM
                    bn_suggested_program
                WHERE
                    DATE(added_date) >= DATE('{self.start_date}') AND DATE(added_date) <= DATE('{self.end_date}')
                    AND user_id = a.id AND program_id IN(
                        34,
                        108,
                        92,
                        75,
                        37,
                        35,
                        36,
                        134,
                        38,
                        73,162,163
                    )
                LIMIT 1
            ) AS sugg_program_name,(
                SELECT
                    sessions
                FROM
                    bn_suggested_program
                WHERE
                    DATE(added_date) >= DATE('{self.start_date}') AND DATE(added_date) <= DATE('{self.end_date}') 
                    AND user_id = a.id AND program_id IN(
                        34,
                        108,
                        92,
                        75,
                        37,
                        35,
                        36,
                        134,
                        38,
                        73,162,163
                    )
                LIMIT 1
            ) AS sugg_program_days,(
                SELECT
                    amount
                FROM
                    bn_suggested_program
                WHERE
                    DATE(added_date) >= DATE('{self.start_date}') AND DATE(added_date) <= DATE('{self.end_date}')
                    AND user_id = a.id AND program_id IN(
                        34,
                        108,
                        92,
                        75,
                        37,
                        35,
                        36,
                        134,
                        38,
                        73,162,163
                    )
                LIMIT 1
            ) AS sugg_amount, a.user_status,
            (SELECT admin_user.crm_user FROM admin_user WHERE admin_user.admin_id=a.mentor_id) as mentor_name ,
            round((SELECT weight_monitor_record_22.weight from weight_monitor_record_22 WHERE weight_monitor_record_22.user_id=a.id and weight_monitor_record_22.is_deleted=0 ORDER by weight_monitor_record_22.wmr_id desc limit 1),2) as last_weight
            FROM
                registries AS a

            WHERE
                  a.user_status IN(
                    'Active',
                    'notstarted',
                    'cleanseactive',
                    'Dormant',
                    'Onhold'
                ) and a.id not in (SELECT userid FROM order_details WHERE program_status = 4  and  DATE(extended_date)>=DATE(now()))
                  AND a.mentor_id NOT IN (0, 1, 196, '')
             GROUP BY
                id
                ) AS ash

            WHERE mentor_name IS NOT NULL	 
            GROUP BY Mentor;


        """
    return query

  def leadBasicStackUpgradeQuery(self):
    query = f"""
        SELECT au.first_name AS Mentor, COUNT(DISTINCT od.userid) AS Total,
        COUNT(DISTINCT od1.email_id) AS `Upgrade`,
        COUNT(DISTINCT od.email_id) - COUNT(DISTINCT od1.userid) AS `Not Upgrade`
        FROM 
        (SELECT DATE(DATE) AS `date`, userid, order_id, email_id, mentor_id 
        FROM order_details
        WHERE order_type = 'New' AND program_type = 1 GROUP BY userid) od
        LEFT JOIN (SELECT DATE(DATE) AS `date`, order_id, userid, email_id, program_type FROM order_details 
        WHERE program_type = 0 GROUP BY userid) od1
        ON (od.userid = od1.userid 
        AND od.order_id < od1.order_id 
        )
        INNER JOIN (select admin_id, first_name FROM admin_user WHERE admin_id != 196
        ) au
        ON au.admin_id = od.mentor_id 
        WHERE 
        DATE(od.date) >= DATE('{self.start_date}') AND 
        DATE(od.date) <= DATE('{self.end_date}') 
        GROUP BY au.first_name;
        """
    return query

  def ocrBasicStackUpgradeQuery(self):
    query = f"""
        SELECT au.first_name AS Mentor, COUNT(DISTINCT od.userid) AS Total,
        COUNT(DISTINCT od1.email_id) AS `Upgrade`,
        COUNT(DISTINCT od.email_id) - COUNT(DISTINCT od1.userid) AS `Not Upgrade`
        FROM 
        (SELECT DATE(DATE) AS `date`, userid, order_id, email_id, mentor_id 
        FROM order_details
        WHERE order_type = 'OMR' AND program_type = 1) od        
        LEFT JOIN (SELECT DATE(DATE) AS `date`, order_id, userid, email_id, program_type FROM order_details 
        WHERE program_type = 0) od1
        ON (od.userid = od1.userid 
        AND od.order_id < od1.order_id 
        )
        INNER JOIN (select admin_id, first_name FROM admin_user 
        ) au
        ON au.admin_id = od.mentor_id 
        WHERE DATE(od.date) >= DATE('{self.start_date}') AND 
        DATE(od.date) <= DATE('{self.end_date}')
        GROUP BY au.first_name;
        """
    return query

  def ocrClientSummaryQuery(self):
    query = f"""
            SELECT Mentor,COUNT(*) AS Total from (SELECT a.id,
            au.first_name AS mentor
            FROM registries AS a JOIN order_details od
            ON a.id=od.userid
            JOIN admin_user AS au ON a.mentor_id=au.admin_id
            WHERE a.user_status IN ('Dropouts', 'Completeds', 'fs','Completed',
            'Dropout','Dropoutss','Completedss')
            GROUP BY id) as t1 group by mentor
            HAVING mentor NOT IN ('Admin', 'Nikita', 'Sadaf', 'Jyoti', 'NO MENTOR', 'NikitaK');
         """
    return query

  def allactiveClientSummaryQuery(self):
    query = f"""
                SELECT
            (
                SELECT
                    first_name
                FROM
                    admin_user
                WHERE
                    admin_id = registries.mentor_id
            ) AS Mentor,
            COUNT(registries.id) AS All_Active,
            (
                SELECT
                    COUNT(rg.id)
                FROM
                    registries rg
                    JOIN order_details od ON od.userid = rg.id
                WHERE
                    od.program_status = 1
                    AND LCASE(rg.user_status) IN ('active')
                    AND DATE(od.extended_date) >= DATE(NOW())
                    AND rg.mentor_id = registries.mentor_id
            ) AS Active,
            (
                SELECT
                    COUNT(rg.id)
                FROM
                    registries rg
                    JOIN order_details od ON od.userid = rg.id
                WHERE
                    od.program_status = 1
                    AND LCASE(rg.user_status) IN ('notstarted')
                    AND DATE(od.extended_date) >= DATE(NOW())
                    AND rg.mentor_id = registries.mentor_id
            ) AS Notstarted,
            (
                SELECT
                    COUNT(rg.id)
                FROM
                    registries rg
                    JOIN order_details od ON od.userid = rg.id
                WHERE
                    od.program_status = 1
                    AND LCASE(rg.user_status) IN ('cleanseactive')
                    AND DATE(od.extended_date) >= DATE(NOW())
                    AND rg.mentor_id = registries.mentor_id
            ) AS Cleanseactive,
            (
                SELECT
                    COUNT(rg.id)
                FROM
                    registries rg
                    JOIN order_details od ON od.userid = rg.id
                WHERE
                    od.program_status = 1
                    AND LCASE(rg.user_status) IN ('onhold')
                    AND DATE(od.extended_date) >= DATE(NOW())
                    AND rg.mentor_id = registries.mentor_id
            ) AS Onhold,
                (
                    SELECT
                        COUNT(rg.id)
                    FROM
                        registries rg
                        JOIN order_details od ON od.userid = rg.id
                    WHERE
                        od.program_status = 1
                        AND LCASE(rg.user_status) IN ('dormant')
                        AND DATE(od.extended_date) >= DATE(NOW())
                        AND rg.mentor_id = registries.mentor_id
                ) AS Dormant
            FROM
                registries
                JOIN order_details ON order_details.userid = registries.id
            WHERE
                LCASE(registries.user_status) IN (
                    'active',
                    'cleanseactive',
                    'dormant',
                    'onhold',
                    'notstarted',
                    'not started'
                )
                AND order_details.program_status = 1
                AND DATE(order_details.extended_date) >= DATE(NOW())
                AND registries.mentor_id NOT IN ('', '0', '10', '196')
            GROUP BY
                registries.mentor_id

            ORDER BY Mentor
            """
    return query

  def activePregPlatClientSummaryQuery(self):
    query = f'''
                    SELECT
                (
                SELECT
                    first_name
                FROM
                    admin_user
                WHERE
                    admin_id = registries.mentor_id
            ) AS Mentor,
            COUNT(registries.id) AS Total,

            (
                SELECT
                    COUNT(rg.id)
                FROM
                    registries rg JOIN order_details od ON od.userid = rg.id 

                   WHERE od.program_status = 1 AND LCASE(rg.user_status) IN('active') and date(od.extended_date)>=date(now()) AND rg.mentor_id = registries.mentor_id) AS Active,

            (
                SELECT
                    COUNT(userid)
                FROM
                    order_details
                WHERE
                    program_name LIKE '%plati%' AND program_status IN(1,2) AND DATE(extended_date) >= date(CURDATE()) AND mentor_id = registries.mentor_id and userid in ( SELECT id from registries WHERE
                        user_status IN(
                            'Active',
                            'cleanseactive',
                            'Dormant',
                            'Onhold',
                            'notstarted',
                            'not started'
                        ))) AS Platinum,
                    (
                    SELECT
                        COUNT(userid)
                    FROM
                        order_details
                    WHERE
                        program_name LIKE '%preg%' AND program_status IN(1,2) AND DATE(extended_date) >= date(CURDATE()) AND mentor_id = registries.mentor_id and userid in ( SELECT id from registries WHERE
                        user_status IN(
                            'Active',
                            'cleanseactive',
                            'Dormant',
                            'Onhold',
                            'notstarted',
                            'not started'
                        )) ) AS Pregancy
                    FROM
                        registries JOIN order_details ON order_details.userid = registries.id
                    WHERE
                        registries.user_status IN(
                            'Active',
                            'cleanseactive',
                            'Dormant',
                            'Onhold',
                            'notstarted',
                            'not started'
                        ) and order_details.program_status in (1,2) and date(order_details.extended_date)>=date(now()) and registries.mentor_id not in ('','0','10','196')
                    GROUP BY
                        Mentor;
        '''
    return query

  def comCallSummaryReport(self):
    query = f'''
                SELECT mentor AS Mentor, 
        COUNT(user_id) AS Total,        
        SUM(CASE WHEN user_id IN (SELECT user_id FROM bn_welcome_appointment 
        WHERE call_type IN (100, 10, 11, 45) AND DATE(added_date) >= DATE('{self.start_date}')) THEN 1 ELSE 0 END) AS `Scheduled`,
        SUM(CASE WHEN user_id NOT IN (SELECT user_id FROM bn_welcome_appointment 
        WHERE call_type IN (100, 10, 11, 45) AND DATE(added_date) >= DATE('{self.start_date}')) THEN 1 ELSE 0 END) AS `Not Scheduled`        
        FROM (        
        SELECT (SELECT first_name FROM admin_user WHERE admin_id = cm.new_mentor) AS mentor,cm.user_id,
        (SELECT user_status FROM registries r WHERE r.id = cm.user_id) AS user_status
        FROM change_of_mentor cm
        LEFT JOIN change_of_mentor cm1
        ON cm.user_id = cm1.user_id AND cm.id < cm1.id
        WHERE cm1.id IS NULL AND cm.old_mentor IN (163)
        and date(cm.added_date) >= date('{self.start_date}') 
        GROUP by cm.user_id
        HAVING user_status IN ('Active',
                'notstarted',
                'cleanseactive',
                'Dormant',
                'Onhold')) AS ash
        GROUP BY ash.mentor
        HAVING `Not Scheduled` > 0;
        '''
    return query

  def halfTimeFeedbackSummaryQuery(self):
    query = f'''
            SELECT Mentor,
            SUM(CASE WHEN mentor_star_rating = 5 THEN 1 ELSE 0 END) AS `5 Ratings`,
            SUM(CASE WHEN mentor_star_rating = 4 THEN 1 ELSE 0 END) AS `4 Ratings`,
            SUM(CASE WHEN mentor_star_rating = 3 THEN 1 ELSE 0 END) AS `3 Ratings`,
            SUM(CASE WHEN mentor_star_rating = 2 THEN 1 ELSE 0 END) AS `2 Ratings`,
            SUM(CASE WHEN mentor_star_rating = 1 THEN 1 ELSE 0 END) AS `1 Rating`
            FROM (SELECT CONCAT(r.first_name,'',r.last_name) as Name,
            r.email_id,
            r.phone AS phone,
            mentor_star_rating,
            au.first_name as Mentor,
            ht.added_date 
            FROM registries r
            INNER JOIN bn_halftime_feedback ht 
            ON ht.user_id = r.id 
            INNER JOIN admin_user au
            ON au.admin_id = r.mentor_id
            WHERE r.mentor_id NOT IN (196, 0) AND DATE(ht.added_date) >= DATE('{self.start_date}')
            AND DATE(ht.added_date) <= DATE('{self.end_date}') AND mentor_star_rating <= 5
            GROUP BY r.email_id) AS sheet
            GROUP BY Mentor
        '''
    return query

  def finalFeedbackSummaryQuery(self):
    query = f'''
        SELECT
          Mentor,
          SUM(
            CASE WHEN rate_mentor = 5 THEN 1 ELSE 0 END
          ) AS `5 Ratings`,
          SUM(
            CASE WHEN rate_mentor = 4 THEN 1 ELSE 0 END
          ) AS `4 Ratings`,
          SUM(
            CASE WHEN rate_mentor = 3 THEN 1 ELSE 0 END
          ) AS `3 Ratings`,
          SUM(
            CASE WHEN rate_mentor = 2 THEN 1 ELSE 0 END
          ) AS `2 Ratings`,
          SUM(
            CASE WHEN rate_mentor = 1 THEN 1 ELSE 0 END
          ) AS `1 Rating`
        FROM
          (
            SELECT
              CONCAT(r.first_name, '', r.last_name) AS Name,
              r.email_id,
              r.phone AS phone,
              ht.rate_mentor,
              au.first_name AS Mentor,
              ht.added_date
            FROM
              registries r
              INNER JOIN bn_final_feedback ht ON ht.user_id = r.id
              INNER JOIN admin_user au ON au.admin_id = r.mentor_id
            WHERE
              r.mentor_id NOT IN (196, 0)
              AND DATE(ht.added_date) >= DATE('{self.start_date}')
                    AND DATE(ht.added_date) <= DATE('{self.end_date}')
              AND ht.rate_mentor <= 5
                GROUP BY r.email_id
          ) AS sheet
        GROUP BY
          Mentor
        '''
    return query

  def newLeadWithoutRefIndianNRI(self):
    query = f'''
        SELECT
        `Name`,
        COUNT(DISTINCT clean_phone) AS `Total Assigned Leads`,
        SUM(CASE WHEN `Indian/NRI` = 'Indian' THEN 1 ELSE 0 END) AS `Assigned Indian Leads`,
        SUM(CASE WHEN `Indian/NRI` = 'NRI' THEN 1 ELSE 0 END) AS `Assigned NRI Leads`,
        SUM(paid_status) AS `Total Paid Leads`,
        SUM(CASE WHEN `Indian/NRI` = 'Indian' AND paid_status = 1 THEN 1 ELSE 0 END) AS `Total Paid Indians`,
        SUM(CASE WHEN `Indian/NRI` = 'NRI' AND paid_status = 1 THEN 1 ELSE 0 END) AS `Total Paid NRI`,
        SUM(CASE WHEN paid_status = 0 THEN 1 ELSE 0 END) AS `Total Un-Paid Leads`,
        SUM(CASE WHEN `Indian/NRI` = 'Indian' AND paid_status = 0 THEN 1 ELSE 0 END) AS `Total Un-Paid Indians`,
        SUM(CASE WHEN `Indian/NRI` = 'NRI' AND paid_status = 0 THEN 1 ELSE 0 END) AS `Total Un-Paid NRI`

        FROM
        (SELECT       
          lm.clean_phone,
          la.assign_to AS `Name`,	
          CASE WHEN (phone_suffix IN (
        SELECT
          RIGHT(
            REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(lm_prev.phone, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            ),
            8
          )
        FROM
          lead_management lm_prev
        WHERE
          DATE(lm_prev.created) < DATE('{self.start_date}'))

      ) THEN 'OL' ELSE 'New Lead' END AS lead_type,
          CASE WHEN
               ((lm.clean_phone LIKE '91%' AND LENGTH(lm.clean_phone) = 12)
                OR (lm.clean_phone LIKE '9191%' AND LENGTH(lm.clean_phone) = 14)
                OR (LENGTH(lm.clean_phone) = 10 AND lm.clean_phone REGEXP '^[6-9][0-9]{{9}}$'))
               THEN 'Indian'
               ELSE 'NRI'
               END AS `Indian/NRI`,
          CASE WHEN lm.email IN (
            SELECT
              email_id
            FROM
              order_details
            WHERE
              program_type = 0 AND DATE(DATE) >= DATE("{self.start_date}")
          )
          OR phone_suffix IN (
            SELECT
              RIGHT(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(mobile_no1, '(', ''),
                        ')',
                        ''
                      ),
                      ' ',
                      ''
                    ),
                    '-',
                    ''
                  ),
                  '+',
                  ''
                ),
                8
              )
            FROM
              billing_details
              INNER JOIN (
                SELECT
                  email_id AS email
                FROM
                  order_details
                WHERE
                  program_type = 0 AND DATE(DATE) >= DATE("{self.start_date}")
              ) AS od2 ON od2.email = email_id
          ) THEN 1 ELSE 0 END AS paid_status
            FROM(
                SELECT		
              DATE(created) AS created,
              id,
              fname,
              email,
              phone, 	
              REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(phone, '(', ''),
                        ')',
                        ''
                      ),
                      ' ',
                      ''
                    ),
                    '-',
                    ''
                  ),
                  '+',
                  ''
                ) AS clean_phone,		
              RIGHT(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(phone, '(', ''),
                        ')',
                        ''
                      ),
                      ' ',
                      ''
                    ),
                    '-',
                    ''
                  ),
                  '+',
                  ''
                ),
                8
              ) AS phone_suffix,			
              enquiry_from
            FROM
              lead_management
                    ) lm
                LEFT JOIN lead_management lm1
                ON (lm.email = lm1.email AND lm.id < lm1.id)
                INNER JOIN (SELECT assign_to, email, id, assign_date FROM lead_action
              WHERE DATE(assign_date) >= DATE('{self.start_date}')) la 
                ON la.email = lm.email
                LEFT JOIN (SELECT id, email FROM lead_action) la1
                ON (la1.email = la.email AND la.id < la1.id)      

            WHERE
                lm1.id IS NULL
                AND la1.id IS NULL             
                AND (lm.enquiry_from NOT LIKE '%Referral%' OR lm.enquiry_from IS NULL)
                AND la.assign_to NOT IN (
                    'Client', 'Client Services',
                    'Nikita', 'NikitaK', 'Select', 'Vrushali',
                    'Saloni', 'Nidhi', 'Chanchal', 'Khyati',
                    'Shubhangi', 'Ayushi'
                )
                AND LOWER(lm.email) NOT LIKE "%test%"

        GROUP BY lm.phone_suffix) AS sheet
        WHERE lead_type = 'New Lead'
        GROUP BY `Name`
        ORDER BY `Total Assigned Leads` DESC
        '''
    return query

  def oldLeadWithoutRefIndianNRI(self):
    query = f'''
            SELECT
            `Name`,
            COUNT(DISTINCT clean_phone) AS `Total Assigned Leads`,
            SUM(CASE WHEN `Indian/NRI` = 'Indian' THEN 1 ELSE 0 END) AS `Assigned Indian Leads`,
            SUM(CASE WHEN `Indian/NRI` = 'NRI' THEN 1 ELSE 0 END) AS `Assigned NRI Leads`,
            SUM(paid_status) AS `Total Paid Leads`,
            SUM(CASE WHEN `Indian/NRI` = 'Indian' AND paid_status = 1 THEN 1 ELSE 0 END) AS `Total Paid Indians`,
            SUM(CASE WHEN `Indian/NRI` = 'NRI' AND paid_status = 1 THEN 1 ELSE 0 END) AS `Total Paid NRI`,
            SUM(CASE WHEN paid_status = 0 THEN 1 ELSE 0 END) AS `Total Un-Paid Leads`,
            SUM(CASE WHEN `Indian/NRI` = 'Indian' AND paid_status = 0 THEN 1 ELSE 0 END) AS `Total Un-Paid Indians`,
            SUM(CASE WHEN `Indian/NRI` = 'NRI' AND paid_status = 0 THEN 1 ELSE 0 END) AS `Total Un-Paid NRI`

            FROM
            (SELECT       
              lm.clean_phone,
              la.assign_to AS `Name`,	
              CASE WHEN (phone_suffix IN (
            SELECT
              RIGHT(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(lm_prev.phone, '(', ''),
                        ')',
                        ''
                      ),
                      ' ',
                      ''
                    ),
                    '-',
                    ''
                  ),
                  '+',
                  ''
                ),
                8
              )
            FROM
              lead_management lm_prev
            WHERE
              DATE(lm_prev.created) < DATE('{self.start_date}'))	
          ) THEN 'OL' ELSE 'New Lead' END AS lead_type,
              CASE WHEN
                   ((lm.clean_phone LIKE '91%' AND LENGTH(lm.clean_phone) = 12)
                    OR (lm.clean_phone LIKE '9191%' AND LENGTH(lm.clean_phone) = 14)
                    OR (LENGTH(lm.clean_phone) = 10 AND lm.clean_phone REGEXP '^[6-9][0-9]{{9}}$'))
                   THEN 'Indian'
                   ELSE 'NRI'
                   END AS `Indian/NRI`,
              CASE WHEN lm.email IN (
                SELECT
                  email_id
                FROM
                  order_details
                WHERE
                  program_type = 0 AND DATE(DATE) >= DATE("{self.start_date}")
              )
              OR phone_suffix IN (
                SELECT
                  RIGHT(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(mobile_no1, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ),
                    8
                  )
                FROM
                  billing_details
                  INNER JOIN (
                    SELECT
                      email_id AS email
                    FROM
                      order_details
                    WHERE
                      program_type = 0 AND DATE(DATE) >= DATE("{self.start_date}")
                  ) AS od2 ON od2.email = email_id
              ) THEN 1 ELSE 0 END AS paid_status
                FROM(
                    SELECT		
                  DATE(created) AS created,
                  id,
                  fname,
                  email,
                  phone, 	
                  REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(phone, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ) AS clean_phone,		
                  RIGHT(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(phone, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ),
                    8
                  ) AS phone_suffix,			
                  enquiry_from
                FROM
                  lead_management
                        ) lm
                    LEFT JOIN lead_management lm1
                    ON (lm.email = lm1.email AND lm.id < lm1.id)
                    INNER JOIN (SELECT assign_to, email, id, assign_date FROM lead_action
                  WHERE DATE(assign_date) >= DATE('{self.start_date}')) la 
                    ON la.email = lm.email
                    LEFT JOIN (SELECT id, email FROM lead_action) la1
                    ON (la1.email = la.email AND la.id < la1.id)      

                WHERE
                    lm1.id IS NULL
                    AND la1.id IS NULL             
                    AND (lm.enquiry_from NOT LIKE '%Referral%' OR lm.enquiry_from IS NULL)
                    AND la.assign_to NOT IN (
                        'Client', 'Client Services',
                        'Nikita', 'NikitaK', 'Select', 'Vrushali',
                        'Saloni', 'Nidhi', 'Chanchal', 'Khyati',
                        'Shubhangi', 'Ayushi'
                    )
                    AND LOWER(lm.email) NOT LIKE "%test%"

            GROUP BY lm.phone_suffix) AS sheet
            WHERE lead_type = 'OL'
            GROUP BY `Name`
            ORDER BY `Total Assigned Leads` DESC
            '''
    return query

  def socialMediaNewleadSummary(self):
    query = f'''
        SELECT assignedTo AS `Name`,                                   
        COUNT(paid_status) AS Assigned,                                
        SUM(paid_status) AS Sales                                      
        FROM                                                           
        (SELECT sl.assignedTo, sl.leadNumber, sl.leadType, sl.sourcet, 
        CASE WHEN                                                      
        RIGHT(                                                         
                REPLACE(                                           
                  REPLACE(                                        
                    REPLACE(                                     
                      REPLACE(                                  
                        REPLACE(sl.leadNumber, '(', ''),       
                        ')',                                   
                        ''                                     
                      ),                                        
                      ' ',                                      
                      ''                                        
                    ),                                           
                    '-',                                         
                    ''                                           
                  ),                                              
                  '+',                                            
                  ''                                              
                ),                                                 
                8                                                  
              ) IN (                                                
            SELECT                                                   
              RIGHT(                                                
                REPLACE(                                           
                  REPLACE(                                        
                    REPLACE(                                     
                      REPLACE(                                  
                        REPLACE(mobile_no1, '(', ''),          
                        ')',                                   
                        ''                                     
                      ),                                        
                      ' ',                                      
                      ''                                        
                    ),                                           
                    '-',                                         
                    ''                                           
                  ),                                              
                  '+',                                            
                  ''                                              
                ),                                                 
                8                                                  
              )                                                     
            FROM                                                     
              billing_details                                       
              INNER JOIN (                                          
                SELECT                                             
                  email_id AS email                               
                FROM                                               
                  order_details                                   
                WHERE                                              
                  program_type = 0                                
              ) AS od2 ON od2.email = email_id) THEN 1 ELSE 0 END AS paid_status

        FROM sociallead sl                                             
        WHERE sl.leadType = 'New'                                      
        AND DATE(sl.created) >= DATE(DATE_FORMAT(NOW(), "%Y-%m-01"))   
        GROUP BY                                                       
        RIGHT(                                                         
                REPLACE(                                           
                  REPLACE(                                        
                    REPLACE(                                     
                      REPLACE(                                  
                        REPLACE(sl.leadNumber, '(', ''),       
                        ')',                                   
                        ''                                     
                      ),                                        
                      ' ',                                      
                      ''                                        
                    ),                                           
                    '-',                                         
                    ''                                           
                  ),                                              
                  '+',                                            
                  ''                                              
                ),                                                 
                8                                                  
              )                                                     
        ) AS sheet                                                     
        GROUP BY assignedTo 

        HAVING `Name` IN ("Akansha", "Krishna", "UrmilaR", "PrajaktaT", "Deeba", "Vidhanshi", 'Barkha', 'KajalS')    
        ORDER BY Assigned DESC  


        '''
    return query

  def socialMediaNewLeadAssignedToday(self):
    query = f'''
        SELECT sl.assignedTo AS `Name`, COUNT(*) AS Counts FROM sociallead sl
        WHERE sl.leadType = 'New' AND DATE(sl.created) = DATE(NOW())
        GROUP BY sl.assignedTo      
        ORDER BY Counts DESC                                            
        '''
    return query

  def consultationCallBookedYesterdayByLeads(self):
    query = f'''
        SELECT
          COUNT(DISTINCT phone) AS Counts
        FROM
          lead_management lm
        WHERE
          enquiry_from LIKE '%consul%'
          AND DATE(created) >=
          CASE 
          WHEN DAYOFWEEK(NOW()) = 2 THEN DATE(NOW() - INTERVAL 2 DAY)
          ELSE DATE(NOW() - INTERVAL 1 DAY)
          END
          AND(
            SELECT
              COUNT(email)
            FROM
              lead_management
            WHERE
              email = lm.email
              AND enquiry_from LIKE '%consul%'
          ) = 1
          AND email NOT IN(
            SELECT
              email_id
            FROM
              order_details
          )
          AND email IN(
            SELECT
              email
            FROM
              lead_action
          )
            AND (email NOT LIKE '%@balancenutrition.in%' OR email NOT LIKE '%test%');
        '''
    return query

  def previousDayUnassignedHS(self):
    query = f'''
        SELECT
          COUNT(DISTINCT phone) AS Counts
        FROM
          lead_management lm
        WHERE
          enquiry_from LIKE '%BN health%'
          AND DATE(created) >= 
          CASE 
          WHEN DAYOFWEEK(NOW()) = 2 
          THEN DATE(NOW() - INTERVAL 2 DAY)
          ELSE DATE(NOW() - INTERVAL 1 DAY)
          END	
          AND(
            SELECT
              COUNT(email)
            FROM
              lead_management
            WHERE
              email = lm.email
              AND enquiry_from LIKE '%BN health%'
          ) = 1
          AND (email NOT IN(
            SELECT
              email_id
            FROM
              order_details
          )
          AND email NOT IN(
            SELECT
              email
            FROM
              lead_action
          )	
          AND stage IN (3, 4) 
            AND (LOWER(email) NOT LIKE '%@balancenutrition.in%' OR LOWER(email) NOT LIKE '%test%'));
        '''
    return query

  def previousDayUnassignedRegistration(self):
    query = f'''
        SELECT
          COUNT(DISTINCT phone) AS Counts
        FROM
          lead_management lm
        WHERE
          enquiry_from LIKE '%registra%'
          AND DATE(created) >= 
          CASE WHEN
          DAYOFWEEK(NOW()) = 2 THEN DATE(NOW() - INTERVAL 2 DAY)
          ELSE DATE(NOW() - INTERVAL 1 DAY)
          END
          AND(
            SELECT
              COUNT(email)
            FROM
              lead_management
            WHERE
              email = lm.email
              AND enquiry_from LIKE '%registra%'
          ) = 1
          AND email NOT IN(
            SELECT
              email_id
            FROM
              order_details
          )
          AND email NOT IN(
            SELECT
              email
            FROM
              lead_action
          )
          AND email NOT IN(
            SELECT
              email_id
            FROM
              order_details
          ) AND (email NOT LIKE '%@balancenutrition.in%' OR email NOT LIKE '%test%');
        '''
    return query

  def yesterdayAllHS(self):
    query = f'''
        SELECT
          COUNT(DISTINCT phone) AS Counts
        FROM
          lead_management lm
        WHERE
          enquiry_from LIKE '%BN health%'
          AND DATE(created) >=
          CASE
          WHEN
          DAYOFWEEK(NOW()) = 2 THEN DATE(NOW() - INTERVAL 2 DAY)
          ELSE DATE(NOW() - INTERVAL 1 DAY)
          END
          AND(
            SELECT
              COUNT(email)
            FROM
              lead_management
            WHERE
              email = lm.email
              AND enquiry_from LIKE '%BN health%'
          ) = 1
          AND email NOT IN(
            SELECT
              email_id
            FROM
              order_details
          ) AND (email NOT LIKE '%@balancenutrition.in%' OR email NOT LIKE '%test%');
        '''
    return query


class dataSheetQueries:

  def __init__(self, start_date, end_date):
    self.start_date = start_date
    self.end_date = end_date

  def tailendDataSheetQuery(self):
    query = f"""
        SELECT * FROM
        (SELECT
            rg.id AS user_id,
            CONCAT(rg.first_name, ' ', rg.last_name) AS full_name,
            rg.first_name,
            rg.email_id,
            (
            SELECT
                order_id
            FROM
                order_details
            WHERE
                program_status = 1 AND userid = rg.id
            ORDER BY
                order_id
            DESC
        LIMIT 1
        ) AS order_id, rg.user_status, rg.my_wallet,(
            SELECT
                REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(mobile_no1, '(', ''), ')', ''), ' ', ''), '-', ''), '+', '')
            FROM
                billing_details
            WHERE
                user_id = rg.id
            ORDER BY
                billing_id
            DESC
        LIMIT 1
        ) AS phone,(
            SELECT
                COUNT(order_id)
            FROM
                order_details
            WHERE
                order_type = 'Renewal' AND userid = rg.id
        ) AS renewal_count,
        (
            (
            SELECT
                SUM(program_session)
            FROM
                order_details
            WHERE
                userid = rg.id
            GROUP BY
                userid
        ) -(
            SELECT
                COUNT(DISTINCT(SESSION))
            FROM
                diet_session_log
            WHERE
                user_id = rg.id AND is_deleted = 0 AND diet_status = '4'
        )
        ) AS pending_sessions,
        (
            SELECT
                COUNT(order_id)
            FROM
                order_details
            WHERE
                userid = rg.id
        ) AS progrme_number,
        (
            SELECT
                first_name
            FROM
                admin_user
            WHERE
                admin_id = rg.mentor_id 
        ) AS mentor,
        (
            SELECT
                userid
            FROM
                order_details
            WHERE
                userid = rg.id AND program_type = 1 AND userid NOT IN(
                SELECT
                    userid
                FROM
                    order_details
                WHERE
                    program_type = 0
            )
        ORDER BY
            order_id
        DESC
        LIMIT 1
        ) AS cleanse_purchase,(SELECT suggested_program FROM bn_suggested_program WHERE user_id = rg.id 
        AND DATE(added_date) >= DATE('{self.start_date}') AND DATE(added_date) <= DATE('{self.end_date}')
        ORDER BY added_date DESC LIMIT 1) as pitched_program,
        (SELECT user_id FROM bn_suggested_program WHERE user_id = rg.id 
         AND DATE(added_date) >= DATE('{self.start_date}') AND DATE(added_date) <= DATE('{self.end_date}')

        ORDER BY added_date DESC LIMIT 1) as pitched_id,
        (SELECT user_id FROM bn_suggested_program WHERE user_id = rg.id 
        AND DATE(added_date) >= DATE('{self.start_date}') AND DATE(added_date) <= DATE('{self.end_date}') 
        AND lead_status like '%Pitch1%' 
        ORDER BY added_date DESC LIMIT 1) as first_pitched 
        FROM
            registries rg
        WHERE
            rg.user_status IN(
                'active',
                'dormant',
                'onhold',
                'premaintenance',
                'maintenance',
                'notstarted',
                'not started'
            ) AND(
                (
                SELECT
                    SUM(program_session)
                FROM
                    order_details
                WHERE
                    userid = rg.id
                GROUP BY
                    userid
            ) -(
            SELECT
                COUNT(DISTINCT(SESSION))
            FROM
                diet_session_log
            WHERE
                user_id = rg.id AND is_deleted = 0 AND diet_status = '4'
        )
            ) <= 3 AND rg.id NOT IN(
            SELECT
                userid
            FROM
                order_details
            WHERE
                program_status IN(4)
        ) ) AS datas                
        HAVING Mentor NOT IN ('Nikita') 
        AND pitched_program IS NULL OR REPLACE(pitched_program, " ", "") IN ("");
         """
    return query

  def leadWithoutRefUnPaidAssignedDataSheetQuery(self):
    query = f'''        
            SELECT
                lm.fname,
                lm.email,  
                lm.clean_phone AS phone,
                la.assign_to, 
                DATE(la.assign_date) AS assign_date
            FROM
                (SELECT fname, email, phone,
                 REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(lm.phone, '(', ''), ')', ''), ' ', ''), '-', ''), '+', '') AS clean_phone,
                 RIGHT(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(lm.phone, '(', ''), ')', ''), ' ', ''), '-', ''), '+', ''), 8) AS phone_suffix
                 FROM lead_management) lm
                LEFT JOIN lead_management lm1
                ON (lm.email = lm1.email AND lm.id < lm1.id)
                LEFT JOIN (SELECT assign_to, email, id, assign_date FROM lead_action) la 
                ON la.email = lm.email
                LEFT JOIN (SELECT id, email FROM lead_action) la1
                ON (la1.email = la.email AND la.id < la1.id)
                LEFT JOIN (SELECT email_id FROM order_details) od
                ON od.email_id = lm.email
                LEFT JOIN (SELECT REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(mobile_no1, '(', ''), ')', ''), ' ', ''), '-', ''), '+', '') AS mobile_no1 FROM billing_details) bd
                ON RIGHT(bd.mobile_no1, 8) = lm.phone_suffix
            WHERE
                lm1.id IS NULL
                AND la1.id IS NULL
                AND (od.email_id IS NULL 
                AND bd.mobile_no1 IS NULL)       
                AND DATE(la.assign_date) >= DATE('{self.start_date}')
                AND DATE(la.assign_date) <= DATE('{self.end_date}')
                AND (lm.enquiry_from NOT LIKE '%Referral%' OR lm.enquiry_from IS NULL)
                AND la.assign_to NOT IN (
                    'Client', 'Client Services',
                    'Nikita', 'NikitaK', 'Select', 'Vrushali',
                    'Saloni', 'Nidhi', 'Chanchal', 'Khyati',
                    'Shubhangi'
                )
            GROUP BY                 
                phone_suffix


        '''

  def activeClientAllPageVisitDataSheetQuery(self):
    query = f'''
        SELECT
          CONCAT(rg.first_name, ' ', rg.last_name) AS name,
          rg.email_id AS email,
          rg.my_wallet,
          (
            SELECT
              REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(mobile_no1, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    )
            FROM
              billing_details
            WHERE
              user_id = rg.id
            ORDER BY
              billing_id DESC
            LIMIT
              1
          ) AS phone,
          pg.program_page AS program_name,
          DATE(pg.added_date) AS added_date,
          rg.id AS user_id,
          rg.user_status,
          (
            SELECT
              suggested_program
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}')) 
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_name,
          (
            SELECT
              sessions
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}'))
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_days,
          (
            SELECT
              amount
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}')) 
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_amount,
          au.crm_user AS mentor
        FROM
          bn_program_page_log pg
          LEFT JOIN registries rg ON rg.id = pg.user_id
          LEFT JOIN admin_user au ON au.admin_id = rg.mentor_id
        WHERE
          pg.page_type IN(1)
          AND rg.user_status IN(
            'Active', 'notstarted', 'cleanseactive', 'Dormant', 'Onhold'
          )
          AND (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}'))
          AND rg.id NOT IN(
            SELECT
              userid
            FROM
              order_details
            WHERE
              DATE(DATE) >= DATE('{self.start_date}') 
              AND DATE(DATE) <= DATE('{self.end_date}')
          )
          AND rg.mentor_id != 196
        GROUP BY
          email
        '''
    return query

  def activeClientCheckoutPageVisitDataSheetQuery(self):
    query = f'''
        SELECT
          CONCAT(rg.first_name, ' ', rg.last_name) AS name,
          rg.email_id AS email,
          rg.my_wallet,
          (
            SELECT
              REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(mobile_no1, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    )
            FROM
              billing_details
            WHERE
              user_id = rg.id
            ORDER BY
              billing_id DESC
            LIMIT
              1
          ) AS phone,
          pg.program_page AS program_name,
          DATE(pg.added_date) AS added_date,
          rg.id AS user_id,
          rg.user_status,
          (
            SELECT
              suggested_program
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}')) 
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_name,
          (
            SELECT
              sessions
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}'))
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_days,
          (
            SELECT
              amount
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}')) 
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_amount,
          au.crm_user AS mentor
        FROM
          bn_program_page_log pg
          LEFT JOIN registries rg ON rg.id = pg.user_id
          LEFT JOIN admin_user au ON au.admin_id = rg.mentor_id
        WHERE
          pg.page_type IN(2)
          AND rg.user_status IN(
            'Active', 'notstarted', 'cleanseactive', 'Dormant', 'Onhold'
          )
          AND (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}'))
          AND rg.id NOT IN(
            SELECT
              userid
            FROM
              order_details
            WHERE
              DATE(DATE) >= DATE('{self.start_date}') 
              AND DATE(DATE) <= DATE('{self.end_date}')
          )
          AND rg.mentor_id != 196
        GROUP BY
          email
        '''
    return query

  def ocrClientsAllPageVisitDataSheetQuery(self):
    query = f'''
                SELECT
          CONCAT(rg.first_name, ' ', rg.last_name) AS name,
          rg.email_id AS email,
          rg.my_wallet,
          (
            SELECT
              REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(mobile_no1, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    )
            FROM
              billing_details
            WHERE
              user_id = rg.id
            ORDER BY
              billing_id DESC
            LIMIT
              1
          ) AS phone,
          pg.program_page AS program_name,
          DATE(pg.added_date) AS added_date,
          rg.id AS user_id,
          rg.user_status,
          (
            SELECT
              suggested_program
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}')) 
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_name,
          (
            SELECT
              sessions
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}'))
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_days,
          (
            SELECT
              amount
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}')) 
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_amount,
          au.crm_user AS mentor
        FROM
          bn_program_page_log pg
          LEFT JOIN registries rg ON rg.id = pg.user_id
          LEFT JOIN admin_user au ON au.admin_id = rg.mentor_id
        WHERE
          pg.page_type IN(1)
          AND rg.user_status NOT IN(
            'Active', 'notstarted', 'cleanseactive', 'Dormant', 'Onhold', 'Inactive'
          )
          AND (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}'))
          AND rg.id NOT IN(
            SELECT
              userid
            FROM
              order_details
            WHERE
              DATE(DATE) >= DATE('{self.start_date}') 
              AND DATE(DATE) <= DATE('{self.end_date}')
          )
          AND rg.mentor_id != 196
        GROUP BY email
        '''
    return query

  def ocrClientsCheckoutPageVisitDataSheetQuery(self):
    query = f'''
                SELECT
          CONCAT(rg.first_name, ' ', rg.last_name) AS name,
          rg.email_id AS email,
          rg.my_wallet,
          (
            SELECT
              REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(mobile_no1, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    )
            FROM
              billing_details
            WHERE
              user_id = rg.id
            ORDER BY
              billing_id DESC
            LIMIT
              1
          ) AS phone,
          pg.program_page AS program_name,
          DATE(pg.added_date) AS added_date,
          rg.id AS user_id,
          rg.user_status,
          (
            SELECT
              suggested_program
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}')) 
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_name,
          (
            SELECT
              sessions
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}'))
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_days,
          (
            SELECT
              amount
            FROM
              bn_suggested_program
            WHERE
            (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}')) 
              AND user_id = rg.id
            LIMIT
              1
          ) AS sugg_program_amount,
          au.crm_user AS mentor
        FROM
          bn_program_page_log pg
          LEFT JOIN registries rg ON rg.id = pg.user_id
          LEFT JOIN admin_user au ON au.admin_id = rg.mentor_id
        WHERE
          pg.page_type IN(2)
          AND rg.user_status NOT IN(
            'Active', 'notstarted', 'cleanseactive', 'Dormant', 'Onhold', 'Inactive'
          )
          AND (DATE(pg.added_date) >= DATE('{self.start_date}') 
          AND DATE(pg.added_date) <= DATE('{self.end_date}'))
          AND rg.id NOT IN(
            SELECT
              userid
            FROM
              order_details
            WHERE
              DATE(DATE) >= DATE('{self.start_date}') 
              AND DATE(DATE) <= DATE('{self.end_date}')
          )
          AND rg.mentor_id != 196
        GROUP BY
          email
        '''
    return query

  def allRateSharedUnpaidSheet(self):
    query = f'''
                SELECT 
        DISTINCT user_id, 
                `Name`, 
                phone, 
                sheet.email_id AS email, 
                my_wallet, 
                old_wallet,
                suggested_program,
                days,
                amount,
                pitched_date,
                mentor,
                user_status,
                payment_mode,
                `payment_link`


        FROM (SELECT m1.user_id, 
        (case WHEN m1.user_id!=0 THEN m1.`name`
        ELSE (
        SELECT CONCAT(fname, ' ', lname)
        FROM `lead_management`
        WHERE `email`=m1.email_id
        ORDER BY id DESC
        LIMIT 1) END) AS Name,

        (case WHEN m1.user_id!=0 THEN (
        SELECT REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(mobile_no1, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            )
        FROM `billing_details`
        WHERE `user_id` = m1.user_id
        ORDER BY billing_id DESC
        LIMIT 1) ELSE (
        SELECT REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(phone, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            )
        FROM `lead_management`
        WHERE `email`=m1.email_id
        ORDER BY id DESC
        LIMIT 1) END) AS phone,
        m1.email_id,
        (SELECT my_wallet FROM registries WHERE id = m1.user_id) AS my_wallet,
        (SELECT old_wallet FROM registries WHERE id = m1.user_id) AS old_wallet,
        m1.suggested_program, 
        m1.sessions AS days, m1.amount, 
        DATE(m1.added_date) AS pitched_date,
        (
        SELECT first_name
        FROM admin_user
        WHERE admin_id = m1.mentor_id) AS mentor, 
        Case when (
        SELECT user_status
        FROM registries
        WHERE email_id = m1.email_id ORDER BY id DESC LIMIT 1) IN ('Active', 'notstarted', 'cleanseactive', 'Dormant', 'Onhold') then 'Active' WHEN (
        SELECT user_status
        FROM registries
        WHERE email_id = m1.email_id ORDER BY id DESC LIMIT 1) IN ('Dropouts', 'Completeds', 'fs', 'Completed', 'Dropout', 'Droputss', 'Completedss') THEN 'OCR' ELSE 'Lead' END AS user_status, 
        m1.payment_mode, 
        m1.payment_link
        FROM bn_suggested_program m1
        LEFT JOIN bn_suggested_program m2 
        ON (m1.email_id = m2.email_id AND m1.id < m2.id)
        WHERE m2.id IS NULL 
        AND m1.lead_status NOT IN('pitch1') 
        AND m1.paid_status NOT IN(1, 2)
        AND (DATE(m1.added_date) >= DATE('{self.start_date}') 
        AND DATE(m1.added_date) <= DATE('{self.end_date}'))) AS sheet

        LEFT JOIN (SELECT email_id FROM order_details WHERE program_type = 0 
        AND (DATE(DATE)>= DATE('{self.start_date}')
        AND DATE(DATE) <= DATE('{self.end_date}'))) od
        ON od.email_id = sheet.email_id
        LEFT JOIN (SELECT mobile_no1 FROM billing_details) bd 
        ON (sheet.user_status = 'Lead' AND 
        RIGHT(
            REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(sheet.phone, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            ),
            8
          ) =
          RIGHT(
            REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(bd.mobile_no1, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            ),
            8
          ))


        WHERE (od.email_id IS NULL AND bd.mobile_no1 IS NULL)

        ;
        '''
    return query

  def counsellorAssignedUnPaidLeadsDataSheetQuery(self):
    query = f'''
                SELECT
            lm.fname AS name,
            lm.email AS email,
            lm.clean_phone AS phone,
            lm.age,
            COALESCE(lm.primary_source, lm.enquiry_from) AS sources,
            lm.country,
            (CASE 
                WHEN 
              lm.clean_phone LIKE '91%' 
                    OR (LENGTH(lm.clean_phone) = 10 AND lm.phone REGEXP '^[6-9][0-9]{9}$')
                THEN 'Indian'
                ELSE 'NRI'
            END) AS 'Indian/NRI',
            lm.overall_health_score AS health_score,
            lm.health_category,  
            lm.status,
            lm.sub_status,    
            DATE(la.fu_date),
            la.fu_note,
            DATE(la.fu_other_date),    
            lm.mentor_comment,
            la.assign_to,
            la.id,
            la.key_insight,
            DATE(la.assign_date) AS assign_date
        FROM (SELECT *, 
      REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, '(', ''), ')', ''), ' ', ''), '-', ''), '+', '') AS clean_phone,
      RIGHT(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, '(', ''), ')', ''), ' ', ''), '-', ''), '+', ''), 8) AS phone_suffix
      FROM lead_management) lm
        LEFT JOIN lead_management lm1
        ON lm.email = lm1.email AND lm.id < lm1.id
        LEFT JOIN lead_action la ON la.email = lm.email 
        LEFT JOIN lead_action la2 ON la.email = la2.email AND la.id < la2.id
        LEFT JOIN (SELECT email_id FROM order_details WHERE program_type = 0) od
        ON od.email_id = lm.email
        LEFT JOIN (SELECT email_id, mobile_no1 FROM billing_details
        INNER JOIN (SELECT email_id AS email FROM order_details WHERE program_type = 0) od
        ON email_id = od.email) bd
        ON	phone_suffix =
          RIGHT(
            REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(bd.mobile_no1, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            ),
            8
          )

        WHERE la2.id IS NULL 
        AND lm1.id IS NULL 
        AND (od.email_id IS NULL
        AND bd.mobile_no1 IS NULL)

            AND (DATE(la.assign_date) >= DATE('{self.start_date}')  
            AND DATE(la.assign_date) <= DATE('{self.end_date}'))
            AND la.assign_to IN ('Akansha')
        GROUP BY phone_suffix


            '''
    return query

  def counsellorAssignedConsultationDoneUnPaidLeadsDataSheetQuery(self):
    query = f'''
                            SELECT
              lm.fname AS name,
              lm.email AS email,
              lm.clean_phone AS phone,
              lm.age,
              COALESCE(
                lm.primary_source, lm.enquiry_from
              ) AS sources,
              lm.country,
              (
                CASE WHEN lm.clean_phone LIKE '91%'
                OR (
                  LENGTH(lm.clean_phone) = 10
                  AND lm.phone REGEXP '^[6-9][0-9]{9}$'
                ) THEN 'Indian' ELSE 'NRI' END
              ) AS 'Indian/NRI',
              lm.overall_health_score AS health_score,
              lm.health_category,
              lm.status,
              lm.sub_status,
              DATE(la.fu_date),
              la.fu_note,
              DATE(la.fu_other_date),
              lm.mentor_comment,
              la.assign_to,
              la.id,
              la.key_insight,
              DATE(la.assign_date) AS assign_date
            FROM
              (
                SELECT
                  *,
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(phone, '(', ''),
                          ')',
                          ''
                        ),
                        ' ',
                        ''
                      ),
                      '-',
                      ''
                    ),
                    '+',
                    ''
                  ) AS clean_phone,
                  RIGHT(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(phone, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ),
                    8
                  ) AS phone_suffix
                FROM
                  lead_management
              ) lm
              LEFT JOIN lead_management lm1 ON lm.email = lm1.email
              AND lm.id < lm1.id
              LEFT JOIN lead_action la ON la.email = lm.email
              LEFT JOIN lead_action la2 ON la.email = la2.email
              AND la.id < la2.id
              LEFT JOIN (
                SELECT
                  email_id
                FROM
                  order_details
                WHERE
                  program_type = 0
              ) od ON od.email_id = lm.email
              LEFT JOIN (
                SELECT
                  email_id,
                  mobile_no1
                FROM
                  billing_details
                  INNER JOIN (
                    SELECT
                      email_id AS email
                    FROM
                      order_details
                    WHERE
                      program_type = 0
                  ) od ON email_id = od.email
              ) bd ON phone_suffix = RIGHT(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(bd.mobile_no1, '(', ''),
                        ')',
                        ''
                      ),
                      ' ',
                      ''
                    ),
                    '-',
                    ''
                  ),
                  '+',
                  ''
                ),
                8
              )
            WHERE
              la2.id IS NULL
              AND lm1.id IS NULL
              AND (
                od.email_id IS NULL
                AND bd.mobile_no1 IS NULL
              )
              AND (
                DATE(la.assign_date) >= DATE('{self.start_date}')
                AND DATE(la.assign_date) <= DATE('{self.end_date}')
              )
              AND la.assign_to IN ('Akansha')
              AND DATE(la.key_insight_date) >= DATE('{self.start_date}')
            GROUP BY
              phone_suffix

        '''
    return query

  def allAssignedUnPaidLeadsDataSheetQuery(self):
    query = f'''
            SELECT 
            created,
            fname,
            gender,
            email,
            phone,
            `source`,
            health_score,
            health_category,
            mentor_comment,
            medical_issue,
            lead_status,
            lead_sub_status,
            key_insight,
            referred_by,
            first_cons,
            suggested_program_details,
            `comment`,
            next_fu_date,
            next_fu_time,
            payment_mode,
            `payment_link`,
            `payment_link_expiry_date`,
            package_amount,
            `prize/offer`,
            mentor
            FROM (SELECT
              DATE(lm.created) AS created,
              lm.fname,
              lm.gender,
              lm.email,
              lm.clean_phone AS phone,
              COALESCE(lm.enquiry_from, lm.primary_source) AS `source`,
              lm.overall_health_score AS health_score,
              lm.health_category AS health_category,
              lm.mentor_comment,
              lm.medical_issue AS medical_issue,
              COALESCE(lm.status, m1.lead_status) AS lead_status,
              COALESCE(lm.sub_status, lm.mentor_sub_status) AS lead_sub_status,
              la.key_insight,
              (
                SELECT
                  CONCAT(
                    first_name, ' ', last_name, '|', id
                  )
                FROM
                  registries
                WHERE
                  email_id = lm.current_url
              ) AS referred_by,
              (
                SELECT
                  CONCAT(
                    COMMENT,
                    '|',
                    DATE_FORMAT(added_date, '%e %b %Y'),
                    '|',
                    (
                      SELECT
                        appointment_slots
                      FROM
                        `bn_book_appointment_slots_mentor`
                      WHERE
                        `id` = slot_id
                    )
                  )
                FROM
                  `bn_welcome_appointment`
                WHERE
                  `name` LIKE CONCAT('%', lm.fname, '%')
                  AND DATE(added_date) >= DATE(lm.created)
                  AND TYPE IN('Lead', 'OldLead')
                  AND order_id = 0
                  AND call_status = 'done'
                ORDER BY
                  id DESC
                LIMIT
                  1
              ) AS first_cons,
              CASE 
              WHEN LENGTH(m1.suggested_program) > 3 
              THEN
              CONCAT(m1.suggested_program, " | " , m1.sessions, " | " , m1.amount)
              ELSE ''
              END 

              AS suggested_program_details,
              CONCAT(
                '(',
                DATEDIFF(NOW(), m1.added_date),
                ' days ago)'
              ) AS suggested_ago,
              m1.comment,
              m1.next_fu_date,
              m1.next_fu_time,
              m1.payment_mode,
              m1.payment_link,
              m1.payment_link_expiry_date,
              ps.package_amount,
              (
                SELECT
                  Prize
                FROM
                  leadclient
                WHERE
                  phone = REPLACE (lm.phone, '-', '')
                LIMIT
                  1
              ) AS `prize/offer`,
              la.assign_to AS mentor,	
              CASE WHEN lm.email IN (
                SELECT
                  email_id
                FROM
                  order_details
                WHERE
                  program_type = 0 
                  AND DATE(DATE) >= DATE(DATE_FORMAT({self.start_date}, "%Y-%m-01"))
              )
              OR phone_suffix IN (
                SELECT
                  RIGHT(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(mobile_no1, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ),
                    8
                  )
                FROM
                  billing_details
                  INNER JOIN (
                    SELECT
                      email_id AS email
                    FROM
                      order_details
                    WHERE
                      program_type = 0 
                      AND DATE(DATE) >= DATE(DATE_FORMAT({self.start_date}, "%Y-%m-01"))
                  ) AS od2 ON od2.email = email_id
              ) THEN 1 ELSE 0 END AS paid_status	
            FROM
              (
                SELECT
                  *,
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(phone, '(', ''),
                          ')',
                          ''
                        ),
                        ' ',
                        ''
                      ),
                      '-',
                      ''
                    ),
                    '+',
                    ''
                  ) AS clean_phone,
                  RIGHT(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(phone, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ),
                    8
                  ) AS phone_suffix
                FROM
                  lead_management
              ) lm
              LEFT JOIN lead_management lm2 ON (
                lm.email = lm2.email
                AND lm.id < lm2.id
              )	
              INNER JOIN lead_action la 
              ON (la.email = lm.email 
              AND DATE(la.assign_date) 
              BETWEEN DATE('{self.start_date}') AND DATE('{self.end_date}'))
              LEFT JOIN lead_action la2 ON (
                la.email = la2.email	AND la.id < la2.id
              )
              LEFT JOIN bn_suggested_program m1
              ON (lm.email = m1.email_id 
              AND DATE(m1.added_date) >= DATE(DATE_FORMAT(NOW(), "%Y-%m-01")))
              LEFT JOIN bn_suggested_program m2
              ON (m1.email_id = m2.email_id AND m1.id < m2.id)
              LEFT JOIN program_session ps 
              ON (m1.program_id = ps.program_id AND m1.sessions = ps.package_sess_duration)	
            WHERE
              lm2.id IS NULL
              AND la2.id IS NULL
              AND m2.id IS NULL	
              AND la.assign_to NOT IN (
                'Client', 'Client Services',
                        'Nikita', 'NikitaK', 'Select', 'Vrushali',
                        'Saloni', 'Nidhi', 'Chanchal', 'Khyati',
                        'Shubhangi'		  
              )	

            GROUP BY
              lm.phone_suffix) AS sheets
            WHERE paid_status = 0

            ;
        '''
    return query

  def wmrReceivedDietNotSendOD(self):
    query = f'''
                    SELECT
                CONCAT(
                    rg.first_name,
                    ' ',
                    rg.last_name, ' User Id: ',        
                    rg.id, ' ',

                    rg.email_id,       
                    (
                    SELECT
                        billing_details.mobile_no1
                    FROM
                        billing_details
                    WHERE
                        billing_details.user_id = rg.id
                    LIMIT 1
                ),    
                rg.user_status    
                ) AS client_details, CONCAT(
                    od.program_name, ' ',       
                    od.program_session * 10,
                    ' Days Mrp : ',
                    od.prog_amt,
                    ' Paid : ',
                    od.amount,
                    'Order type : ',
                    od.order_type
                ) AS program_details,(
                SELECT
                    first_name
                FROM
                    admin_user
                WHERE
                    admin_id = rg.mentor_id
            ) AS mentor,
            DATE_FORMAT(wmr.posted_date, '%d %b %Y') AS posted_date,
            (
                SELECT
                    actual_session
                FROM
                    diet_session_log
                WHERE
                    user_id = rg.id
                ORDER BY
                    diet_id
                DESC
            LIMIT 1
            ) AS send_session, od.program_session AS program_session,(
                CASE WHEN DATEDIFF(DATE(NOW()), wmr.posted_date) = 0 THEN 'Today' WHEN DATEDIFF(DATE(NOW()), wmr.posted_date) = 1 THEN 'Yesterday' ELSE CONCAT(
                    DATEDIFF(DATE(NOW()), wmr.posted_date), ' ', 'Days Ago')
                END
                ) AS cal_days
            FROM
                registries rg
            LEFT JOIN(
                SELECT
                    m1.session,
                    m1.order_id,
                    m1.user_id,
                    m1.wmr_id,
                    m1.session_duration,
                    m1.is_deleted,
                    m1.added_date,
                    m1.posted_date
                FROM
                    weight_monitor_record_22 m1
                LEFT JOIN weight_monitor_record_22 m2 ON
                    (
                        m1.user_id = m2.user_id AND m1.wmr_id < m2.wmr_id
                    )
                WHERE
                    m2.wmr_id IS NULL AND m1.session_duration = 10 AND m1.is_deleted = 0
            ) wmr
            ON
                wmr.user_id = rg.id
            LEFT JOIN order_details od ON
                wmr.order_id = od.order_id
            WHERE
                DATE_FORMAT(wmr.added_date, '%Y-%m-%d') < date((NOW() - INTERVAL 2 DAY)) AND rg.user_status IN('Active') AND(
                    (
                        wmr.session < od.program_session AND rg.id NOT IN(
                        SELECT
                            user_id
                        FROM
                            diet_session_log
                        WHERE
                            order_id = wmr.order_id AND actual_session =(wmr.session +1) AND diet_status = 4 AND is_deleted = 0
                    )
                    ) OR(
                        wmr.session = od.program_session AND wmr.user_id IN(
                        SELECT
                            userid
                        FROM
                            order_details
                        WHERE
                            program_status = 4
                    )
                    )
                ) AND(
                SELECT
                    COUNT(diet_id)
                FROM
                    diet_session_log
                WHERE
                    order_id = od.order_id
            ) < od.program_session AND wmr.session_duration = '10' AND wmr.is_deleted = '0' AND od.program_status = '1' and rg.email_id != 'Ruchi.rawal@gmail.com'
            GROUP BY
                wmr.user_id
            ORDER BY
                wmr.posted_date
            '''
    return query

  def nafReceivedDietNotSendOD(self):
    query = f'''
                    SELECT
                CONCAT(
                    rg.first_name,' ',rg.last_name, ' ',       
                    'User Id: ', rg.id, ' ',       
                    rg.email_id, ' ',        
                    (
                    SELECT
                        billing_details.mobile_no1
                    FROM
                        billing_details
                    WHERE
                        billing_details.user_id = rg.id
                    LIMIT 1
                ),  ' ',  
                rg.user_status    
                ) AS client_details, 
                CONCAT(
                    od.program_name, ' ',        
                    od.program_session * 10, ' ',
                    ' Days Mrp: ',
                    od.prog_amt,
                    ' Paid: ',
                    od.amount,
                    ' Order type: ',
                    od.order_type
                ) AS program_details, CONCAT(
                    DATEDIFF(NOW(), na.created), ' Days Ago') AS days_ago,
                    (
                SELECT
                    DATE_FORMAT(created, '%d %b %Y')
                FROM
                    new_assessment
                WHERE
                    user_id = od.userid AND DATE(created) >= DATE(od.date)
                ORDER BY
                    id
                DESC
            LIMIT 1
            ) AS assessment_date,
              (
                SELECT
                    first_name
                FROM
                    admin_user
                WHERE
                    admin_id = rg.mentor_id
            ) as mentor,
                    rg.last_visited_screen as last_visited_screen,
                    na.id AS naf_id
                FROM
                   (
                       SELECT
                                        *
                                    FROM
                                        order_details
                                    WHERE
                                        order_id IN(
                                        SELECT
                                            MAX(order_id)
                                        FROM
                                            order_details
                                        WHERE program_status = '1'
                                        GROUP BY
                                            userid
                                    )
                                ) od
            LEFT JOIN registries rg ON
                od.userid = rg.id
            LEFT JOIN diet_session_log ds ON
                ds.order_id = od.order_id
            INNER JOIN new_assessment na ON
                na.user_id = od.userid
            WHERE
                (
                    ds.diet_status != '4' OR ds.diet_status IS NULL
                ) AND na.naf_acknowledge = '0' AND DATE_FORMAT(na.created, '%Y-%m-%d') <(DATE(NOW()) - INTERVAL 2 DAY) AND od.order_type IN('New', 'OMR') AND (SELECT COUNT(diet_id) FROM diet_session_log WHERE order_id = od.order_id AND diet_status = 4 AND is_deleted = 0) = 0 AND rg.user_status NOT IN(
                'dormant',
                'dropout',
                'completed',
                'fs',
                'notstarted'
            )  and rg.last_visited_screen Not in ('assessment/1','program-details')  AND rg.email_id NOT LIKE '%test%' and rg.id not in (12433,22843,22842,21402) and od.mentor_id != 196 
            GROUP BY
                rg.id
            ORDER BY
                na.created
            ASC
            '''
    return query

  def mentorAssignedUnPaidIndianLeadsDataSheetQuery(self):
    query = f'''
                SELECT
          DATE(lm.created) AS created,
          lm.fname,
          lm.gender,
          lm.email,
          clean_phone AS phone,
          COALESCE(lm.enquiry_from, lm.primary_source) AS `source`,
          lm.overall_health_score AS health_score,
          lm.health_category AS health_category,
          lm.mentor_comment,
          lm.medical_issue AS medical_issue,
          COALESCE(lm.status, spd.lead_status) AS lead_status,
          COALESCE(
            lm.sub_status, lm.mentor_sub_status
          ) AS lead_sub_status,
          (
            SELECT
              CONCAT(
                first_name, ' ', last_name, '|', id
              )
            FROM
              registries
            WHERE
              email_id = lm.current_url
          ) AS referred_by,
          (
            SELECT
              CONCAT(
                COMMENT,
                '|',
                DATE_FORMAT(added_date, '%e %b %Y'),
                '|',
                (
                  SELECT
                    appointment_slots
                  FROM
                    `bn_book_appointment_slots_mentor`
                  WHERE
                    `id` = slot_id
                )
              )
            FROM
              `bn_welcome_appointment`
            WHERE
              `name` LIKE CONCAT('%', lm.fname, '%')
              AND DATE(added_date) >= DATE(lm.created)
              AND TYPE IN('Lead', 'OldLead')
              AND order_id = 0
              AND call_status = 'done'
            ORDER BY
              id DESC
            LIMIT
              1
          ) AS first_cons,
          spd.suggested_program,
          spd.sessions,
          spd.amount,
          CONCAT(
            '(',
            DATEDIFF(NOW(), spd.added_date),
            ' days ago)'
          ) AS suggested_ago,
          spd.comment,
          spd.next_fu_date,
          spd.next_fu_time,
          spd.payment_mode,
          spd.payment_link,
          spd.payment_link_expiry_date,
          ps.package_amount,
          (
            SELECT
              Prize
            FROM
              leadclient
            WHERE
              phone = REPLACE (lm.phone, '-', '')
            LIMIT
              1
          ) AS `prize/offer`,
          la.assign_to AS mentor
        FROM
          (
            SELECT
              *,
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(phone, '(', ''),
                      ')',
                      ''
                    ),
                    ' ',
                    ''
                  ),
                  '-',
                  ''
                ),
                '+',
                ''
              ) AS clean_phone,
              RIGHT(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(phone, '(', ''),
                        ')',
                        ''
                      ),
                      ' ',
                      ''
                    ),
                    '-',
                    ''
                  ),
                  '+',
                  ''
                ),
                8
              ) AS phone_suffix
            FROM
              lead_management

          ) lm
          LEFT JOIN lead_management lm2 ON (
            lm.email = lm2.email
            AND lm.id < lm2.id
          )
          LEFT JOIN(
            SELECT
              m1.*
            FROM
              bn_suggested_program m1
              LEFT JOIN bn_suggested_program m2 ON (
                m1.email_id = m2.email_id
                AND m1.id < m2.id
              )
            WHERE
              m2.id IS NULL
          ) AS spd ON lm.email = spd.email_id
          LEFT JOIN program_session ps ON spd.program_id = ps.program_id
          AND spd.sessions = ps.package_sess_duration
          LEFT JOIN lead_action la ON la.email = lm.email
          LEFT JOIN lead_action la2 ON (
            la.email = la2.email
            AND la.id < la2.id
          )
          LEFT JOIN (
            SELECT
              email_id
            FROM
              order_details
            WHERE
              program_type = 0
          ) od ON od.email_id = lm.email
          LEFT JOIN (
            SELECT
              mobile_no1
            FROM
              billing_details
          ) bd ON lm.phone_suffix = RIGHT(
            REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(bd.mobile_no1, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            ),
            8
          )
        WHERE
          lm2.id IS NULL
          AND la2.id IS NULL
          AND (lm.clean_phone LIKE '91%'
          OR (LENGTH(lm.clean_phone) = 10 AND lm.clean_phone REGEXP '^[6-9][0-9]{9}$'))
          AND od.email_id IS NULL
          AND bd.mobile_no1 IS NULL
          AND la.assign_to IN (
            'Aasiya', 'Anam', 'Batul', 'Arpita',
            'Chaitali', "Hardi", 'Divya', 'Epshita',
            'Gauhar', 'Gunjan', 'Jyoti', 'Kajal',
            'Nazneen', 'Prajakta', 'PrajaktaT',
            'Rashmi', 'Shirin', 'Sadaf', 'Sahejpreet',
            'Shraddha', 'Urmila', 'UrmilaR',
            'Vartika'
          )  
          AND DATE(la.assign_date) >= DATE('{self.start_date}')
          AND DATE(la.assign_date) <= DATE('{self.start_date}')
        GROUP BY
          lm.phone_suffix;
        '''
    return query

  def mentorAssignedUnPaidNRILeadsDataSheetQuery(self):
    query = f'''
                SELECT
          DATE(lm.created) AS created,
          lm.fname,
          lm.gender,
          lm.email,
          clean_phone AS phone,
          COALESCE(lm.enquiry_from, lm.primary_source) AS `source`,
          lm.overall_health_score AS health_score,
          lm.health_category AS health_category,
          lm.mentor_comment,
          lm.medical_issue AS medical_issue,
          COALESCE(lm.status, spd.lead_status) AS lead_status,
          COALESCE(
            lm.sub_status, lm.mentor_sub_status
          ) AS lead_sub_status,
          (
            SELECT
              CONCAT(
                first_name, ' ', last_name, '|', id
              )
            FROM
              registries
            WHERE
              email_id = lm.current_url
          ) AS referred_by,
          (
            SELECT
              CONCAT(
                COMMENT,
                '|',
                DATE_FORMAT(added_date, '%e %b %Y'),
                '|',
                (
                  SELECT
                    appointment_slots
                  FROM
                    `bn_book_appointment_slots_mentor`
                  WHERE
                    `id` = slot_id
                )
              )
            FROM
              `bn_welcome_appointment`
            WHERE
              `name` LIKE CONCAT('%', lm.fname, '%')
              AND DATE(added_date) >= DATE(lm.created)
              AND TYPE IN('Lead', 'OldLead')
              AND order_id = 0
              AND call_status = 'done'
            ORDER BY
              id DESC
            LIMIT
              1
          ) AS first_cons,
          spd.suggested_program,
          spd.sessions,
          spd.amount,
          CONCAT(
            '(',
            DATEDIFF(NOW(), spd.added_date),
            ' days ago)'
          ) AS suggested_ago,
          spd.comment,
          spd.next_fu_date,
          spd.next_fu_time,
          spd.payment_mode,
          spd.payment_link,
          spd.payment_link_expiry_date,
          ps.package_amount,
          (
            SELECT
              Prize
            FROM
              leadclient
            WHERE
              phone = REPLACE (lm.phone, '-', '')
            LIMIT
              1
          ) AS `prize/offer`,
          la.assign_to AS mentor
        FROM
          (
            SELECT
              *,
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(phone, '(', ''),
                      ')',
                      ''
                    ),
                    ' ',
                    ''
                  ),
                  '-',
                  ''
                ),
                '+',
                ''
              ) AS clean_phone,
              RIGHT(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(phone, '(', ''),
                        ')',
                        ''
                      ),
                      ' ',
                      ''
                    ),
                    '-',
                    ''
                  ),
                  '+',
                  ''
                ),
                8
              ) AS phone_suffix
            FROM
              lead_management

          ) lm
          LEFT JOIN lead_management lm2 ON (
            lm.email = lm2.email
            AND lm.id < lm2.id
          )
          LEFT JOIN(
            SELECT
              m1.*
            FROM
              bn_suggested_program m1
              LEFT JOIN bn_suggested_program m2 ON (
                m1.email_id = m2.email_id
                AND m1.id < m2.id
              )
            WHERE
              m2.id IS NULL
          ) AS spd ON lm.email = spd.email_id
          LEFT JOIN program_session ps ON spd.program_id = ps.program_id
          AND spd.sessions = ps.package_sess_duration
          LEFT JOIN lead_action la ON la.email = lm.email
          LEFT JOIN lead_action la2 ON (
            la.email = la2.email
            AND la.id < la2.id
          )
          LEFT JOIN (
            SELECT
              email_id
            FROM
              order_details
            WHERE
              program_type = 0
          ) od ON od.email_id = lm.email
          LEFT JOIN (
            SELECT
              mobile_no1
            FROM
              billing_details
          ) bd ON lm.phone_suffix = RIGHT(
            REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(bd.mobile_no1, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            ),
            8
          )
        WHERE
          lm2.id IS NULL
          AND la2.id IS NULL
          AND NOT (lm.clean_phone LIKE '91%'
          OR (LENGTH(lm.clean_phone) = 10 AND lm.clean_phone REGEXP '^[6-9][0-9]{9}$'))
          AND od.email_id IS NULL
          AND bd.mobile_no1 IS NULL
          AND la.assign_to IN (
            'Aasiya', 'Anam', 'Batul', 'Arpita',
            'Chaitali', "Hardi", 'Divya', 'Epshita',
            'Gauhar', 'Gunjan', 'Jyoti', 'Kajal',
            'Nazneen', 'Prajakta', 'PrajaktaT',
            'Rashmi', 'Shirin', 'Sadaf', 'Sahejpreet',
            'Shraddha', 'Urmila', 'UrmilaR',
            'Vartika'
          )  
          AND DATE(la.assign_date) >= DATE('{self.start_date}')
          AND DATE(la.assign_date) <= DATE('{self.end_date}')
        GROUP BY
          lm.phone_suffix;
        '''
    return query

  def inductionCallNotDoneDataSheet(self):
    query = f'''
                SELECT
          rg.id,
          CONCAT(rg.first_name, ' ', rg.last_name) AS name,
          rg.email_id AS email,
          rg.my_wallet,
          (
            SELECT
              CONCAT("''", mobile_no1)
            FROM
              billing_details
            WHERE
              user_id = rg.id
            ORDER BY
              billing_id DESC
            LIMIT
              1
          ) AS phone,
          od.program_name,
          DATE(od.date) AS purchase_date,
          rg.user_status,
          au.first_name AS mentor,
          od.order_type,
          od.program_type,
          od.program_session,
          od.prog_duration,
          DATE_FORMAT(od.exp_date, '%D %b %Y') AS exp_date,
          (
            SELECT
              COUNT(user_id)
            FROM
              bn_consultation_call_booking
            WHERE
              counsellor_id = 215
              AND call_status = 'done'
              AND user_id = rg.id
          ) AS call_status,
          (
            SELECT
              CONCAT(
                'Date: ',
                DATE_FORMAT(call_date, '%e %b %Y'),
                '<br>Time: ',
                time_slot
              )
            FROM
              bn_consultation_call_booking
            WHERE
              counsellor_id = 215
              AND user_id = rg.id
              AND call_status IN ('pending', 'reschedule')
            ORDER BY
              id DESC
            LIMIT
              1
          ) AS call_details,
          rg.cs_fu_note
        FROM
          order_details od
          LEFT JOIN registries rg ON od.userid = rg.id
          LEFT JOIN admin_user au ON rg.mentor_id = au.admin_id
        WHERE
          (DATE(od.date) >= DATE('{self.start_date}')
          AND DATE(od.date) <= DATE('{self.end_date}'))
          AND od.order_type IN ('New', 'OMR')
        GROUP BY
          od.userid
        HAVING
          call_status = 0
          AND mentor NOT IN ('Nikita')
        ORDER BY
          od.date DESC
        '''
    return query

  def mentorsNoAdvPurchaseDataSheet(self):
    query = f"""
                SELECT
            CONCAT(a.first_name, ' ', a.last_name) AS Name,
            a.id AS client_id,
            (SELECT concat("''", mobile_no1) FROM billing_details WHERE email_id=a.email_id LIMIT 1) as mobile,
            a.email_id,
            a.my_wallet,
            a.old_wallet,
            (
            SELECT
                suggested_program
            FROM
                bn_suggested_program
            WHERE
                DATE(added_date) BETWEEN DATE('{self.start_date}') AND DATE('{self.end_date}') AND user_id = a.id AND program_id IN(
                    34,
                    108,
                    92,
                    75,
                    37,
                    35,
                    36,
                    134,
                    38,
                    73,162,163
                )
            LIMIT 1
        ) AS sugg_program_name,(
            SELECT
                sessions
            FROM
                bn_suggested_program
            WHERE
                DATE(added_date) BETWEEN DATE('{self.start_date}') AND DATE('{self.end_date}') AND user_id = a.id AND program_id IN(
                    34,
                    108,
                    92,
                    75,
                    37,
                    35,
                    36,
                    134,
                    38,
                    73,162,163
                )
            LIMIT 1
        ) AS sugg_program_days,(
            SELECT
                amount
            FROM
                bn_suggested_program
            WHERE
                DATE(added_date) BETWEEN DATE('{self.start_date}') AND DATE('{self.end_date}') AND user_id = a.id AND program_id IN(
                    34,
                    108,
                    92,
                    75,
                    37,
                    35,
                    36,
                    134,
                    38,
                    73,162,163
                )
            LIMIT 1
        ) AS sugg_amount, a.user_status,
        (SELECT admin_user.crm_user FROM admin_user WHERE admin_user.admin_id=a.mentor_id) as mentor
        FROM
            registries AS a

        WHERE
              a.user_status IN(
                'Active',
                'notstarted',
                'cleanseactive',
                'Dormant',
                'Onhold'
            ) and a.id not in (SELECT userid FROM order_details WHERE program_status = 4  and  date(extended_date)>=date(now()))    
         GROUP BY
            id    
         HAVING sugg_program_name IN ("") OR sugg_program_name IS NULL
            ;
        """
    return query

  def mentorNoAdvPurchaseAbove70kgExceptDormantDataSheet(self):
    query = f"""
                SELECT
            CONCAT(a.first_name, ' ', a.last_name) AS Name,
            a.id AS client_id,
            (SELECT concat("''", mobile_no1) FROM billing_details WHERE email_id=a.email_id LIMIT 1) as mobile,
            a.email_id,
            a.my_wallet,
            a.old_wallet,
            (
            SELECT
                suggested_program
            FROM
                bn_suggested_program
            WHERE
                DATE(added_date) BETWEEN DATE('{self.start_date}') AND DATE('{self.end_date}') AND user_id = a.id AND program_id IN(
                    34,
                    108,
                    92,
                    75,
                    37,
                    35,
                    36,
                    134,
                    38,
                    73,162,163
                )
            LIMIT 1
        ) AS sugg_program_name,(
            SELECT
                sessions
            FROM
                bn_suggested_program
            WHERE
                DATE(added_date) BETWEEN DATE('{self.start_date}') AND DATE('{self.end_date}') AND user_id = a.id AND program_id IN(
                    34,
                    108,
                    92,
                    75,
                    37,
                    35,
                    36,
                    134,
                    38,
                    73,162,163
                )
            LIMIT 1
        ) AS sugg_program_days,(
            SELECT
                amount
            FROM
                bn_suggested_program
            WHERE
                DATE(added_date) BETWEEN DATE('{self.start_date}') AND DATE('{self.end_date}') AND user_id = a.id AND program_id IN(
                    34,
                    108,
                    92,
                    75,
                    37,
                    35,
                    36,
                    134,
                    38,
                    73,162,163
                )
            LIMIT 1
        ) AS sugg_amount, a.user_status,
        (SELECT admin_user.crm_user FROM admin_user WHERE admin_user.admin_id=a.mentor_id) as mentor,
round((SELECT weight_monitor_record_22.weight from weight_monitor_record_22 WHERE weight_monitor_record_22.user_id=a.id 
       and weight_monitor_record_22.is_deleted=0 ORDER by weight_monitor_record_22.wmr_id desc limit 1),2) as last_weight
        FROM
            registries AS a

        WHERE
              a.user_status IN(
                'Active',
                'notstarted',
                'cleanseactive',
                'Dormant',
                'Onhold'
            ) and a.id not in (SELECT userid FROM order_details WHERE program_status = 4  and  date(extended_date)>=date(now())) 
              and a.user_status Not IN('Dormant')
         GROUP BY
            id    
         HAVING last_weight >=70 AND (sugg_program_name IN ("") OR sugg_program_name IS NULL)
            ;
        """
    return query

  def goodWeightLossClient(self):
    query = f'''
                    SELECT
                rg.id,
                CONCAT(rg.first_name, ' ', rg.last_name) AS Name,
                rg.email_id,
               CONCAT("''",
                (
                SELECT

                        mobile_no1

                FROM
                    billing_details
                WHERE
                    user_id = rg.id
                ORDER BY
                    billing_id
                DESC
            LIMIT 1
            )
            ) AS phone, rg.user_status,(
                SELECT
                    first_name
                FROM
                    admin_user
                WHERE
                    admin_id = rg.mentor_id
            ) AS mentor,
            (ROUND(( SELECT weight FROM weight_monitor_record_22 WHERE user_id = rg.id and order_id=od.order_id and is_deleted=0 ORDER BY wmr_id DESC  LIMIT 1 )-( SELECT weight FROM weight_monitor_record_22 WHERE user_id = rg.id and order_id=od.order_id and is_deleted=0 ORDER BY wmr_id ASC LIMIT 1 ), 2)) as loss
            FROM
                registries rg JOIN order_details od on rg.email_id=od.email_id
            WHERE
            od.program_status=1 and  rg.user_status NOT IN(
                    'Completed',
                    'Completeds',
                    'Completedss',
                    'fs',
                    'Dropout',
                    'Dropouts',
                    'Dropoutss',
                    'Inactive'
                ) and ABS( ( SELECT weight FROM weight_monitor_record_22 WHERE user_id = rg.id and order_id=od.order_id and is_deleted=0 ORDER BY wmr_id DESC  LIMIT 1 )-( SELECT weight FROM weight_monitor_record_22 WHERE user_id = rg.id and order_id=od.order_id and is_deleted=0 ORDER BY wmr_id ASC LIMIT 1 ) ) >=5
               HAVING loss < 0;
        '''
    return query

  def leadBasicStackNotUpgradedDataSheet(self):
    query = f'''
                SELECT
          od.userid AS client_id,
          (
            SELECT
              first_name
            FROM
              registries
            WHERE
              id = od.userid
          ) AS Name,
          od.email_id,
          od.program_name,
          od.extended_date,
          (
            SELECT
              first_name
            FROM
              admin_user
            WHERE
              admin_id = mentor_id			
          ) AS mentor
        FROM
          order_details od
        WHERE
          mentor_id != 196 AND
          order_type = 'New'
          AND DATE(DATE) >= DATE('{self.start_date}') AND DATE(date) <= DATE('{self.end_date}')
          AND program_type = '1'
          AND userid NOT IN (
            SELECT
              userid
            FROM
              order_details
            WHERE
              userid = od.userid
              AND order_id > od.order_id
              AND program_type = 0
          )
        GROUP BY
          email_id;
        '''
    return query

  def ocrBasicStackNotUpgradedDataSheet(self):
    query = f'''
                SELECT

          (
            SELECT
              first_name
            FROM
              registries
            WHERE
              id = od.userid
          ) AS Name,
          od.email_id,
          od.program_name,
          od.extended_date,
          od.userid AS client_id,
          (
            SELECT
              first_name
            FROM
              admin_user
            WHERE
              admin_id = mentor_id
          ) AS mentor
        FROM
          order_details od
        WHERE
          mentor_Id != 196 AND
          order_type = 'OMR'
          AND DATE(DATE) >= DATE('{self.start_date}')
            AND DATE(date) <= DATE('{self.end_date}')
          AND program_type = '1'
          AND userid NOT IN (
            SELECT
              userid
            FROM
              order_details
            WHERE
              userid = od.userid
              AND order_id > od.order_id
              AND program_type = 0
          )
        GROUP BY
          email_id;
        '''
    return query

  def comCallNotDoneDataSheet(self):
    query = f'''
                 SELECT (SELECT first_name FROM admin_user WHERE admin_id = cm.new_mentor) AS mentor,
         cm.user_id,
         (SELECT user_status FROM registries r WHERE r.id = cm.user_id) AS user_status,
         (SELECT r.first_name FROM registries r WHERE r.id = cm.user_id) AS first_name,
        (SELECT r.last_name FROM registries r WHERE r.id = cm.user_id) AS last_name,
        (SELECT r.email_id FROM registries r WHERE r.id = cm.user_id) AS email
        FROM change_of_mentor cm
        LEFT JOIN change_of_mentor cm1
        ON cm.user_id = cm1.user_id AND cm.id < cm1.id
        WHERE cm1.id IS NULL AND cm.old_mentor IN (163)  
        AND cm.user_id NOT IN (SELECT user_id FROM bn_welcome_appointment 
        WHERE call_type IN (100, 10, 11, 45) AND DATE(added_date) >= DATE('{self.start_date}')) and date(cm.added_date) >= date('{self.start_date}') GROUP by user_id
        HAVING user_status IN ('Active',
                'notstarted',
                'cleanseactive',
                'Dormant',
                'Onhold')



        '''
    return query

  def halfTimeFeedbackDataSheet(self):
    query = f'''
            SELECT CONCAT(r.first_name,'',r.last_name) as Name,
            r.email_id,
            CONCAT("''", r.phone) AS phone,
            mentor_star_rating, 
            ht.improvement_needed AS improvement_needed,
            au.first_name as mentor,
            DATE(ht.added_date) AS added_date 
            FROM registries r
            INNER JOIN bn_halftime_feedback ht 
            ON ht.user_id = r.id 
            INNER JOIN admin_user au
            ON au.admin_id = r.mentor_id
            WHERE r.mentor_id NOT IN (196, 0) AND DATE(ht.added_date) >= DATE('{self.start_date}')
            AND DATE(ht.added_date) <= DATE('{self.end_date}') AND mentor_star_rating <= 5
            GROUP BY r.email_id
            ;
            '''
    return query

  def finalFeedbackDataSheet(self):
    query = f'''
            SELECT CONCAT(r.first_name,'',r.last_name) as Name,
            r.email_id,
            CONCAT("''", r.phone) AS phone,
            ht.rate_mentor, 
            ht.improvement_needed AS improvement_needed,
            au.first_name as mentor,
            DATE(ht.added_date) AS added_date 
            FROM registries r
            INNER JOIN bn_final_feedback ht 
            ON ht.user_id = r.id 
            INNER JOIN admin_user au
            ON au.admin_id = r.mentor_id
            WHERE r.mentor_id NOT IN (196, 0) AND DATE(ht.added_date) >= DATE('{self.start_date}')
            AND DATE(ht.added_date) <= DATE('{self.end_date}') AND ht.rate_mentor <= 5
            GROUP BY r.email_id
            ;
            '''
    return query


class mentorAuditQueries:

  def __init__(self, userId):
    self.userId = userId

  def statusSummary(self):
    query = f'''
        SELECT user_status AS `User Status`,COUNT(id) AS Counts 
        FROM `registries` WHERE mentor_id = {self.userId} 
        AND user_status IN ('Active','cleanseactive','Dormant','Onhold','notstarted','not started') 
        GROUP BY user_status;
        '''
    return query

  def notStartedClientQuery(self):
    query = f'''
                SELECT
        Name,
        email_id,
        program,
        start_date,
        exp_date FROM (SELECT (
        SELECT
                first_name
            FROM
                admin_user
            WHERE
                admin_id = mentor_id
        ) AS Mentor,
            CONCAT(first_name, ' ', last_name) AS Name,
            email_id,
            (
                CASE WHEN(
                SELECT
                    CONCAT(
                        program_name,
                        ' (',
                        program_session,
                        ' Ssn)'
                    )
                FROM
                    order_details
                WHERE
                    userid = id AND program_status = 1
            ) IS NOT NULL THEN(
            SELECT
                CONCAT(
                    program_name,
                    ' (',
                    program_session,
                    ' Ssn)'
                )
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                CONCAT(
                    program_name,
                    ' (',
                    program_session,
                    ' Ssn)'
                )
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
            END
        ) AS program,(
            CASE WHEN(
            SELECT
                DATE_FORMAT(start_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) IS NOT NULL THEN(
            SELECT
                DATE_FORMAT(start_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                DATE_FORMAT(start_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
        END
        ) AS start_date,
        (
            CASE WHEN(
            SELECT
                DATE_FORMAT(extended_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) IS NOT NULL THEN(
            SELECT
                DATE_FORMAT(extended_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                DATE_FORMAT(extended_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
        END
        ) AS exp_date,
        (
        CASE WHEN (CASE WHEN(
            SELECT
                start_date
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) IS NOT NULL THEN(
            SELECT
                start_date
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                start_date
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
        END) < DATE(NOW()) THEN 1
        ELSE 0
        END
        ) AS not_started_OD
        FROM
            `registries`
        WHERE
            mentor_id = {self.userId} AND user_status = 'notstarted' 
        ORDER BY
            (
                CASE WHEN(
                SELECT
                    DATE_FORMAT(start_date, '%d-%m-%Y')
                FROM
                    order_details
                WHERE
                    userid = id AND program_status = 1
            ) IS NOT NULL THEN(
            SELECT
                DATE(start_date) 
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                DATE(start_date)
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
            END
        ) ASC ) AS datas
        WHERE not_started_OD = 0

        '''
    return query

  def notStartedODclientQuery(self):
    query = f'''
                SELECT 
        Name,
        email_id,
        program,
        start_date,
        exp_date FROM (SELECT (
        SELECT
                first_name
            FROM
                admin_user
            WHERE
                admin_id = mentor_id
        ) AS Mentor,
            CONCAT(first_name, ' ', last_name) AS Name,
            email_id,
            (
                CASE WHEN(
                SELECT
                    CONCAT(
                        program_name,
                        ' (',
                        program_session,
                        ' Ssn)'
                    )
                FROM
                    order_details
                WHERE
                    userid = id AND program_status = 1
            ) IS NOT NULL THEN(
            SELECT
                CONCAT(
                    program_name,
                    ' (',
                    program_session,
                    ' Ssn)'
                )
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                CONCAT(
                    program_name,
                    ' (',
                    program_session,
                    ' Ssn)'
                )
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
            END
        ) AS program,(
            CASE WHEN(
            SELECT
                DATE_FORMAT(start_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) IS NOT NULL THEN(
            SELECT
                DATE_FORMAT(start_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                DATE_FORMAT(start_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
        END
        ) AS start_date,
        (
            CASE WHEN(
            SELECT
                DATE_FORMAT(extended_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) IS NOT NULL THEN(
            SELECT
                DATE_FORMAT(extended_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                DATE_FORMAT(extended_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
        END
        ) AS exp_date,
        (
        CASE WHEN (CASE WHEN(
            SELECT
                start_date
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) IS NOT NULL THEN(
            SELECT
                start_date
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                start_date
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
        END) < DATE(NOW()) THEN 1
        ELSE 0
        END
        ) AS not_started_OD
        FROM
            `registries`
        WHERE
            mentor_id = {self.userId} AND user_status = 'notstarted' 
        ORDER BY
            (
                CASE WHEN(
                SELECT
                    DATE_FORMAT(start_date, '%d-%m-%Y')
                FROM
                    order_details
                WHERE
                    userid = id AND program_status = 1
            ) IS NOT NULL THEN(
            SELECT
                DATE(start_date) 
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) ELSE(
            SELECT
                DATE(start_date)
            FROM
                order_details
            WHERE
                userid = id AND program_status = 4
            ORDER BY
                start_date ASC
            LIMIT 1
        )
            END
        ) ASC ) AS datas
        WHERE not_started_OD = 1

        '''
    return query

  def dormantclientQuery(self):
    query = f'''
                SELECT
            CONCAT(first_name, ' ', last_name) AS NAME,
            email_id,
            (
            SELECT
                CONCAT(
                    program_name,
                    ' (',
                    program_session,
                    ' Ssn)'
                )
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) AS program,
        (
            SELECT
                DATE_FORMAT(exp_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) AS default_expiry_date,
        (
            SELECT
                DATE_FORMAT(extended_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                userid = id AND program_status = 1
        ) AS extended_expiry_date,
        (
            SELECT
                DATE_FORMAT(
                    DATE(start_date) + INTERVAL 10 DAY,
                    '%d-%m-%Y'
                )
            FROM
                diet_session_log
            WHERE
                user_id = id AND order_id =(
                SELECT
                    order_id
                FROM
                    order_details
                WHERE
                    userid = id AND program_status = 1
            )
        ORDER BY
            diet_id
        DESC
        LIMIT 1
        ) AS weight_update_pending_since
        FROM
            `registries`
        WHERE
            `mentor_id` = {self.userId} AND `user_status` = 'Dormant' AND CURDATE() >=(
            SELECT
                (
                    DATE(start_date) - INTERVAL 19 DAY
                )
            FROM
                diet_session_log
            WHERE
                user_id = id AND order_id =(
                SELECT
                    order_id
                FROM
                    order_details
                WHERE
                    userid = id AND program_status = 1
            )
        ORDER BY
            diet_id
        DESC
        LIMIT 1
        );

        '''
    return query

  def onholdClientQuery(self):
    query = f'''
                SELECT         
        `NAME`,
        email_id,
        program,
        expiry_date,
        break_end_date

        FROM (SELECT

            CONCAT(first_name, ' ', last_name) AS NAME,
            email_id,
            (
            SELECT
                CONCAT(
                    program_name,
                    ' (',
                    program_session,
                    ' Ssn)'
                )
            FROM
                order_details
            WHERE
                program_status = 1 AND userid = id
        ) AS program,
        (
            SELECT
                DATE_FORMAT(extended_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                program_status = 1 AND userid = rg.id
        ) AS expiry_date,
        (
            SELECT
                DATE_FORMAT(end_date, '%d-%m-%Y')
            FROM
                onhold_clients oc
            WHERE
                order_id =(
                SELECT
                    order_id
                FROM
                    order_details
                WHERE
                    program_status = 1 AND userid = rg.id
            )
        ORDER BY
            oc.id
        DESC
        LIMIT 1
        ) AS break_end_date,

        (
        CASE WHEN DATE((
            SELECT
                end_date
            FROM
                onhold_clients oc
            WHERE
                order_id =(
                SELECT
                    order_id
                FROM
                    order_details
                WHERE
                    program_status = 1 AND userid = rg.id
            )
        ORDER BY
            oc.id
        DESC
        LIMIT 1
        )) < DATE(NOW()) THEN 1
        ELSE 0
        END
        ) AS is_onholdOD
        FROM
            `registries` rg
        WHERE
            `mentor_id` = {self.userId} AND user_status = 'Onhold'
        ORDER BY
            (
            SELECT
                DATE(end_date)
            FROM
                onhold_clients oc
            WHERE
                order_id =(
                SELECT
                    order_id
                FROM
                    order_details
                WHERE
                    program_status = 1 AND userid = rg.id
            )
        ORDER BY
            oc.id
        DESC
        LIMIT 1
        ) ASC) AS sheet
        WHERE is_onholdOD = 0;


        '''
    return query

  def onholdODclientQuery(self):
    query = f'''
                SELECT        
        `NAME`,
        email_id,
        program,
        expiry_date,
        break_end_date

        FROM (SELECT
        (
        SELECT first_name
            FROM
                admin_user
            WHERE
                admin_id = mentor_id
        ) AS Mentor,
            CONCAT(first_name, ' ', last_name) AS NAME,
            email_id,
            (
            SELECT
                CONCAT(
                    program_name,
                    ' (',
                    program_session,
                    ' Ssn)'
                )
            FROM
                order_details
            WHERE
                program_status = 1 AND userid = id
        ) AS program,
        (
            SELECT
                DATE_FORMAT(extended_date, '%d-%m-%Y')
            FROM
                order_details
            WHERE
                program_status = 1 AND userid = rg.id
        ) AS expiry_date,
        (
            SELECT
                DATE_FORMAT(end_date, '%d-%m-%Y')
            FROM
                onhold_clients oc
            WHERE
                order_id =(
                SELECT
                    order_id
                FROM
                    order_details
                WHERE
                    program_status = 1 AND userid = rg.id
            )
        ORDER BY
            oc.id
        DESC
        LIMIT 1
        ) AS break_end_date,

        (
        CASE WHEN DATE((
            SELECT
                end_date
            FROM
                onhold_clients oc
            WHERE
                order_id =(
                SELECT
                    order_id
                FROM
                    order_details
                WHERE
                    program_status = 1 AND userid = rg.id
            )
        ORDER BY
            oc.id
        DESC
        LIMIT 1
        )) < DATE(NOW()) THEN 1
        ELSE 0
        END
        ) AS is_onholdOD
        FROM
            `registries` rg
        WHERE
            `mentor_id` = {self.userId} AND user_status = 'Onhold'
        ORDER BY
            (
            SELECT
                DATE(end_date)
            FROM
                onhold_clients oc
            WHERE
                order_id =(
                SELECT
                    order_id
                FROM
                    order_details
                WHERE
                    program_status = 1 AND userid = rg.id
            )
        ORDER BY
            oc.id
        DESC
        LIMIT 1
        ) ASC) AS sheet
        WHERE is_onholdOD = 1;

        '''
    return query


class impQueryTemplete:

  def __init__(self, query):
    self.query = query

  nri_status = '''
        CASE WHEN
        ((lm.clean_phone LIKE '91%' AND LENGTH(lm.clean_phone) = 12)
          OR (lm.clean_phone LIKE '9191%' AND LENGTH(lm.clean_phone) = 14)
          OR (LENGTH(lm.clean_phone) = 10 AND lm.clean_phone REGEXP '^[6-9][0-9]{9}$'))
        THEN 'Indian'
        ELSE 'NRI'
        END AS nri_status
    '''

  lead_type_status = '''
            CASE WHEN ((phone_suffix IN (
        SELECT
          RIGHT(
            REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(lm_prev.phone, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            ),
            8
          )
        FROM
          lead_management lm_prev
        WHERE
          DATE(lm_prev.created) < DATE('2024-12-01')))
          OR 
          (lm.email IN (SELECT email FROM lead_action
                  WHERE EXISTS (
                    SELECT 1 FROM lead_action
                    WHERE email = lm.email AND DATE(assign_date) >= DATE('{self.start_date}')
                                    AND DATE(key_insight_date) < DATE("2024-12-01")
                    )))
      ) THEN 'OL' ELSE 'New Lead' END AS lead_type
    '''

  high_potential_status = '''
        CASE 
      WHEN (NOT((lm.clean_phone LIKE '91%' AND LENGTH(lm.clean_phone) = 12)
      OR (lm.clean_phone LIKE '9191%' AND LENGTH(lm.clean_phone) = 14)
      OR (LENGTH(lm.clean_phone) = 10 AND lm.clean_phone REGEXP '^[6-9][0-9]{9}$')) 
      OR lm.age >= 35) THEN 'Prime Segment'
      WHEN lm.weight_difference >= 8 THEN 'Stage 3-4'
      WHEN 
      (COALESCE(lm.medical_issue,lm.clinical_condition) NOT IN ('')  
      AND COALESCE(lm.medical_issue,lm.clinical_condition) NOT LIKE 'no%'
      ) 
      THEN 'Medical Condition',
      WHEN (LOWER(COALESCE(lm.enquiry_from, lm.primary_source)) LIKE '%insta%'
      OR LOWER(COALESCE(lm.enquiry_from, lm.primary_source)) LIKE '%face%')
      THEN 'Social Media'
      ELSE 'Other'
      END
      AS lead_category    
    '''

  counsellor_consultaiton_status = '''
        CASE 
      WHEN DATE(la.key_insight_date) >= DATE(DATE_FORMAT(NOW(), "%Y-%m-01"))
      THEN 1
      ELSE 0 END AS consultation_status
    '''

  medical_condition_status = '''
        CASE WHEN 
            LENGTH(
            SUBSTR(
                la.key_insight,
                LOCATE("Clinical Condition : ", la.key_insight) + LENGTH("Clinical Condition : "),
                LOCATE("<br>", la.key_insight, LOCATE("Clinical Condition : ", la.key_insight) + LENGTH("Clinical Condition : "))
                - (LOCATE("Clinical Condition : ", la.key_insight) + LENGTH("Clinical Condition : "))
            )
             ) > 0 THEN 1 ELSE 0 END AS medical_status
        '''

  paid_status = '''
            CASE WHEN lm.email IN (
        SELECT
          email_id
        FROM
          order_details
        WHERE
          program_type = 0 AND DATE(DATE) >= DATE("2024-11-01")
      )
      OR phone_suffix IN (
        SELECT
          RIGHT(
            REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(mobile_no1, '(', ''),
                    ')',
                    ''
                  ),
                  ' ',
                  ''
                ),
                '-',
                ''
              ),
              '+',
              ''
            ),
            8
          )
        FROM
          billing_details
          INNER JOIN (
            SELECT
              email_id AS email
            FROM
              order_details
            WHERE
              program_type = 0 AND DATE(DATE) >= DATE("2024-11-01")
          ) AS od2 ON od2.email = email_id
      ) THEN 1 ELSE 0 END AS paid_status
    '''

  key_insight_date = f'''
        DATE_FORMAT(
        STR_TO_DATE(
          REPLACE(
            REPLACE(
              REPLACE(
                REPLACE(
                  SUBSTR(
                    la.key_insight,
                    LOCATE('<b>', la.key_insight) + LENGTH('<b>'),
                    LOCATE('</b>', la.key_insight) - (
                      LOCATE('<b>', la.key_insight) + LENGTH('<b>')
                    )
                  ),
                  'st',
                  ''
                ),
                'nd',
                ''
              ),
              'rd',
              ''
            ),
            'th',
            ''
          ),
          '%d %b %Y'
        ),
        '%Y-%m-%d'
      ) AS keyinsight_date

    '''


class analysisReportQuery:

  def __init__(self, start_date, end_date):
    self.start_date = start_date
    self.end_date = end_date

  def counsellorSalesSummaryQuery(self):
    query = f'''
            SELECT
          first_name AS `NAME`,
          CASE WHEN (
            LOWER(lead_source) LIKE '%whatsapp%'
            OR LOWER(lead_source) LIKE '%khyat%'
            OR LOWER(lead_source) LIKE '%consul%'
            OR LOWER(lead_source) LIKE '%walk%'
            OR LOWER(lead_source) LIKE '%zop%'
            OR LOWER(lead_source) LIKE '%phone enq%'
            OR LOWER(lead_source) LIKE '%ref%'
            OR LOWER(lead_source) LIKE '%insta%'
            OR LOWER(lead_source) LIKE '%face%'
          ) THEN 'High Potential'
          WHEN (
            age >= 35
            AND LOWER(nri_status) LIKE '%indian%'
          ) THEN 'Age 35+' WHEN LOWER(nri_status) LIKE '%nri%' THEN 'NRI' 
           WHEN (
            LOWER(lead_source) LIKE '%health%'
            OR LOWER(lead_source) LIKE '%hs%'
            AND stages IN (3, 4)
          ) 
          THEN 'Stage 3 & 4' 
          ELSE 'Other' END AS `CATEGORY`,
          COUNT(*) AS `SALE`
        FROM
          (
            SELECT
              au.first_name,
              lm.age,
              lm.email AS lead_email,
              lm.clean_phone AS lm_phone,
              od.email_id AS paid_email,
              bd.clean_mobile1 AS paid_mobile,
              lm.lead_source,
              lm.stages,
              CASE WHEN (
                (
                  lm.clean_phone LIKE '91%'
                  AND LENGTH(lm.clean_phone) = 12
                )
                OR (
                  lm.clean_phone LIKE '9191%'
                  AND LENGTH(lm.clean_phone) = 14
                )
                OR (
                  LENGTH(lm.clean_phone) = 10
                  AND lm.clean_phone REGEXP '^[6-9][0-9]{9}$'
                )
              ) THEN 'Indian' ELSE 'NRI' END AS nri_status
            FROM
              (
                SELECT
                  *
                FROM
                  order_details
                WHERE
                  program_type = 0
                  AND DATE(DATE) BETWEEN DATE('{self.start_date}') AND DATE('{self.end_date}')   
                  AND sales_person IN (252, 274, 278, 285,286)
                  AND LOWER(order_type) IN ('New', 'OMR')
                  AND program_duration_days > 14
                  AND LOWER(program_name) NOT LIKE '%dubai%'
                  AND prog_buy_amt IS NOT NULL
              ) od
              INNER JOIN (
                SELECT
                  email_id,
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(mobile_no1, '(', ''),
                          ')',
                          ''
                        ),
                        ' ',
                        ''
                      ),
                      '-',
                      ''
                    ),
                    '+',
                    ''
                  ) AS clean_mobile1,
                  RIGHT(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(mobile_no1, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ),
                    8
                  ) AS mobile1_suffix
                FROM
                  billing_details
              ) bd 
              ON od.email_id = bd.email_id			
              INNER JOIN admin_user au 
              ON au.admin_id = od.sales_person			
              LEFT JOIN (
                SELECT
                  id,
                  age,
                  email,
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(phone, '(', ''),
                          ')',
                          ''
                        ),
                        ' ',
                        ''
                      ),
                      '-',
                      ''
                    ),
                    '+',
                    ''
                  ) AS clean_phone,
                  RIGHT(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(phone, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ),
                    8
                  ) AS phone_suffix,
                  COALESCE(
                    primary_source, enquiry_from, 'Other'
                  ) AS lead_source,
                  CASE WHEN CAST(
                    weight_difference AS DECIMAL(4, 2)
                  ) BETWEEN 0
                  AND 2 THEN 1 WHEN CAST(
                    weight_difference AS DECIMAL(4, 2)
                  ) BETWEEN 3
                  AND 7 THEN 2 WHEN CAST(
                    weight_difference AS DECIMAL(4, 2)
                  ) BETWEEN 8
                  AND 15 THEN 3 WHEN CAST(
                    weight_difference AS DECIMAL(4, 2)
                  ) > 15 THEN 4 ELSE 'No Stage' END AS stages
                FROM
                  lead_management
              ) lm 
              ON (lm.phone_suffix = bd.mobile1_suffix OR lm.email = bd.email_id)
              LEFT JOIN lead_management lm1 ON lm1.email = lm.email
              AND lm.id < lm1.id			
            WHERE
              lm1.id IS NULL
            GROUP BY paid_email
          ) AS sub_data
        GROUP BY
          `NAME`,
          CATEGORY

        '''
    return query

  def cousellorLeadAnalysisDataQuery(self):
    query = f'''
            SELECT
          sub_data.*,
          CASE WHEN (
            LOWER(lead_source) LIKE '%whatsapp%'
            OR LOWER(lead_source) LIKE '%khyat%'
            OR LOWER(lead_source) LIKE '%consul%'
            OR LOWER(lead_source) LIKE '%walk%'
            OR LOWER(lead_source) LIKE '%zop%'
            OR LOWER(lead_source) LIKE '%phone enq%'
            OR LOWER(lead_source) LIKE '%ref%'
            OR LOWER(lead_source) LIKE '%insta%'
            OR LOWER(lead_source) LIKE '%face%'
          ) THEN 'High Potential' WHEN LOWER(nri_status) LIKE '%nri%' THEN 'NRI' WHEN (
            age >= 35
            AND LOWER(nri_status) LIKE '%indian%'
          ) THEN 'Age 35+' WHEN (
            LOWER(lead_source) LIKE '%health%'
            OR LOWER(lead_source) LIKE '%hs%'
            AND stages IN (3, 4)
          ) THEN 'Stage 3 & 4' ELSE 'Other' END AS lead_category
        FROM
          (
            SELECT
              lm.email,
              lm.clean_phone,
              lm.age,
              COALESCE(
                lm.primary_source, lm.enquiry_from
              ) AS lead_source,
              CASE WHEN (
                (
                  phone_suffix IN (
                    SELECT
                      RIGHT(
                        REPLACE(
                          REPLACE(
                            REPLACE(
                              REPLACE(
                                REPLACE(lm_prev.phone, '(', ''),
                                ')',
                                ''
                              ),
                              ' ',
                              ''
                            ),
                            '-',
                            ''
                          ),
                          '+',
                          ''
                        ),
                        8
                      )
                    FROM
                      lead_management lm_prev
                    WHERE
                      DATE(lm_prev.created) < 
                      DATE(DATE_FORMAT('{self.start_date}', "%Y-%m-01"))
                  )
                )
                OR (
                  lm.email IN (
                    SELECT
                      email
                    FROM
                      lead_action
                    WHERE
                      EXISTS (
                        SELECT
                          1
                        FROM
                          lead_action
                        WHERE
                          email = lm.email
                          AND DATE(key_insight_date) < 
                          DATE(DATE_FORMAT('{self.start_date}', "%Y-%m-01"))
                      )
                  )
                )
              ) THEN 'OL' ELSE 'New Lead' END AS lead_type,
              CASE WHEN CAST(
                lm.weight_difference AS DECIMAL(4, 2)
              ) BETWEEN 0
              AND 2 THEN 1 WHEN CAST(
                lm.weight_difference AS DECIMAL(4, 2)
              ) BETWEEN 3
              AND 7 THEN 2 WHEN CAST(
                lm.weight_difference AS DECIMAL(4, 2)
              ) BETWEEN 8
              AND 15 THEN 3 WHEN CAST(
                lm.weight_difference AS DECIMAL(4, 2)
              ) > 15 THEN 4 ELSE 'No Stage' END AS stages,
              CASE WHEN (
                (
                  lm.clean_phone LIKE '91%'
                  AND LENGTH(lm.clean_phone) = 12
                )
                OR (
                  lm.clean_phone LIKE '9191%'
                  AND LENGTH(lm.clean_phone) = 14
                )
                OR (
                  LENGTH(lm.clean_phone) = 10
                  AND lm.clean_phone REGEXP '^[6-9][0-9]{{9}}$'
                )
              ) THEN 'Indian' ELSE 'NRI' END AS nri_status,
              la.assign_to,
              CASE WHEN DATE(la.key_insight_date) >=
              DATE(DATE_FORMAT('{self.start_date}', "%Y-%m-01")) 
              THEN 1 ELSE 0 END AS cons_status,
              CASE WHEN (
                lm.email IN (
                  SELECT
                    email_id
                  FROM
                    order_details
                  WHERE
                    program_type = 0
                    AND DATE(DATE) BETWEEN 
                    DATE(DATE_FORMAT('{self.start_date}', "%Y-%m-01"))
                    AND DATE('{self.end_date}')))
                OR phone_suffix IN (
                  SELECT
                    RIGHT(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(
                              REPLACE(mobile_no1, '(', ''),
                              ')',
                              ''
                            ),
                            ' ',
                            ''
                          ),
                          '-',
                          ''
                        ),
                        '+',
                        ''
                      ),
                      8
                    )
                  FROM
                    billing_details
                    INNER JOIN (
                      SELECT
                        email_id AS email
                      FROM
                        order_details
                      WHERE
                        program_type = 0
                        AND DATE(DATE) BETWEEN 
                        DATE(
                          DATE_FORMAT('{self.start_date}', "%Y-%m-01")
                        )
                        AND DATE('{self.end_date}')

                    ) AS od2 ON od2.email = email_id
                )
               THEN 1 ELSE 0 END AS paid_status
            FROM
              (
                SELECT
                  *,
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(phone, '(', ''),
                          ')',
                          ''
                        ),
                        ' ',
                        ''
                      ),
                      '-',
                      ''
                    ),
                    '+',
                    ''
                  ) AS clean_phone,
                  RIGHT(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(phone, '(', ''),
                            ')',
                            ''
                          ),
                          ' ',
                          ''
                        ),
                        '-',
                        ''
                      ),
                      '+',
                      ''
                    ),
                    8
                  ) AS phone_suffix
                FROM
                  lead_management
              ) lm
              LEFT JOIN lead_management lm2 ON (
                lm.email = lm2.email
                AND lm.id < lm2.id
              )
              INNER JOIN lead_action la ON la.email = lm.email
              LEFT JOIN lead_action la1 ON la.email = la1.email
              AND la.id < la1.id
            WHERE
              lm2.id IS NULL
              AND la1.id IS NULL
                    AND LOWER(lm.email) NOT LIKE '%test%' 
                        AND LENGTH(lm.clean_phone) > 4
              AND la.assign_to IN (
                'Akansha', 'Deeba', 'ShraddhaK', 'Krishna', 'Barkha'
              )
              AND DATE(la.assign_date) BETWEEN DATE(
                DATE_FORMAT('{self.start_date}', "%Y-%m-01")
              )
              AND DATE('{self.end_date}')	

            GROUP BY
              lm.phone_suffix
          ) AS sub_data
        '''
    return query

  def counsellorSmLeadSummaryQuery(self):
    query = f'''
        SELECT 
        assignedTo AS `NAME`,
        COUNT(DISTINCT leadNumber) AS `TOTAL`,
        SUM(paid_status) AS `SALE`
        FROM (SELECT 
        sl.*,
        CASE WHEN RIGHT(sl.sociallead_phone, 8) IN (
            SELECT RIGHT(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(mobile_no1, '(', ''),
                                ')',
                                ''
                            ),
                            ' ',
                            ''
                        ),
                        '-',
                        ''
                    ),
                    '+',
                    ''
                ),
                8
            )
            FROM billing_details
            INNER JOIN (
                SELECT email_id AS email
                FROM order_details
                WHERE program_type = 0
                AND DATE(date) >= DATE("{self.start_date}")
            ) AS od2 ON od2.email = email_id
        ) THEN 1 ELSE 0 END AS paid_status
        FROM (
            SELECT *,
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(leadNumber, '(', ''),
                            ')',
                            ''
                        ),
                        ' ',
                        ''
                    ),
                    '-',
                    ''
                ),
                '+',
                ''
            ) AS sociallead_phone
            FROM sociallead
            WHERE DATE(created) BETWEEN DATE("{self.start_date}") AND DATE("{self.end_date}")
        ) AS sl
        WHERE sl.assignedTo IN ('Akansha', 'Krishna', 'Deeba', 'Barkha')
        GROUP BY leadNumber) AS sheet
        GROUP BY assignedTo
    '''
    return query
