-- ====================================================================
-- GYM MEMBERSHIP CHURN & RETENTION ANALYTICS
-- Database Engine: PostgreSQL 17.5
-- Author: Javier Eduardo Heredia Beltran
-- ====================================================================

-- 1. Churn Rate and Revenue Loss (MRR) Calculation by Plan Tier

SELECT 
    plan_type,
    COUNT(member_id) AS total_members,
    SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END) AS churned_members,
    ROUND(
        CAST(SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END) AS NUMERIC) / COUNT(member_id) * 100, 
        2
    ) AS churn_rate_percent,
    SUM(CASE WHEN status = 'Active' THEN monthly_fee ELSE 0 END) AS active_mrr,
    SUM(CASE WHEN status = 'Churned' THEN monthly_fee ELSE 0 END) AS lost_mrr
FROM members
GROUP BY plan_type
ORDER BY churn_rate_percent DESC;

-- 2. Average Attendance and "Churn Risk" Segmentation

WITH member_activity AS (
    SELECT
	    m.member_id,
		m.full_name,
		m.plan_type,
		m.monthly_fee,
		m.status,
		m.join_date,
		MAX(c.checkin_date) AS last_checkin_date,
		COUNT(c.checkin_id) AS total_visits
	FROM members m
	LEFT JOIN checkins c ON m.member_id = c.member_id
	WHERE m.status = 'Active'
	GROUP BY m.member_id, m.full_name, m.plan_type, m.monthly_fee, m.status, m.join_date
)
SELECT
    plan_type,
	COUNT(member_id) AS active_members,
	SUM(CASE WHEN last_checkin_date < '2026-08-01'::date OR last_checkin_date IS NULL THEN 1 ELSE 0 END) AS high_risk_members,
	ROUND(
        CAST(SUM(CASE WHEN last_checkin_date < '2026-08-01'::date OR last_checkin_date IS NULL THEN 1 ELSE 0 END) AS NUMERIC)
		/ COUNT(member_id) * 100, 2
		) AS risk_percentage,
		SUM(CASE WHEN last_checkin_date < '2026-08-01'::date OR last_checkin_date IS NULL THEN monthly_fee ELSE 0 END) AS mrr_at_risk
		FROM member_activity
		GROUP BY plan_type
		ORDER BY mrr_at_risk DESC;

-- 3. Weekly Attendance Frequency and Preferred Activity Analysis

WITH weekly_checkins AS (
    SELECT 
        m.member_id,
        m.status,
        m.plan_type,
        c.activity_type,
        COUNT(c.checkin_id) AS total_checkins,
        GREATEST(1, ROUND(
            (COALESCE(m.churn_date, '2026-08-20'::date) - m.join_date) / 7.0, 1
        )) AS weeks_active
    FROM members m
    JOIN checkins c ON m.member_id = c.member_id
    GROUP BY m.member_id, m.status, m.plan_type, c.activity_type, m.churn_date, m.join_date
)
SELECT 
    status,
    activity_type,
    COUNT(DISTINCT member_id) AS total_members,
    ROUND(AVG(total_checkins / weeks_active), 2) AS avg_weekly_visits
FROM weekly_checkins
GROUP BY status, activity_type
ORDER BY status, avg_weekly_visits DESC;

-- 4. Support Interactions Impact and Ticket Resolution Times

WITH support_summary AS (
    SELECT 
        m.member_id,
        m.status,
        m.plan_type,
        COUNT(s.interaction_id) AS total_support_tickets,
        AVG(s.resolution_days) AS avg_resolution_time,
        DENSE_RANK() OVER (ORDER BY COUNT(s.interaction_id) DESC) AS ticket_rank
    FROM members m
    LEFT JOIN support_interactions s ON m.member_id = s.member_id
    GROUP BY m.member_id, m.status, m.plan_type
)
SELECT 
    status,
    ROUND(AVG(total_support_tickets), 2) AS avg_tickets_per_member,
    ROUND(AVG(avg_resolution_time), 2) AS avg_days_to_resolve_ticket
FROM support_summary
GROUP BY status;