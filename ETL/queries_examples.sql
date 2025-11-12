-- Ejemplos de queries SQL para la base de datos de voleibol

-- ============================================================
-- 1. PARTIDOS GANADOS POR COLOMBIA
-- ============================================================
SELECT 
    m.match_no,
    m.match_date_utc,
    m.match_date_time_local,
    t1.name AS equipo_a,
    t2.name AS equipo_b,
    m.team_a_score,
    m.team_b_score,
    winner.name AS ganador,
    m.city,
    m.country,
    t.name AS torneo
FROM matches m
JOIN teams t1 ON m.team_a_no = t1.no
JOIN teams t2 ON m.team_b_no = t2.no
JOIN teams winner ON m.winner_team_no = winner.no
JOIN tournaments t ON m.tournament_no = t.no
WHERE winner.code = 'COL'  -- Colombia
ORDER BY m.match_date_utc DESC;

-- Alternativa: usando el nombre del país
SELECT 
    m.match_no,
    m.match_date_utc,
    t1.name AS equipo_a,
    t2.name AS equipo_b,
    m.team_a_score,
    m.team_b_score,
    winner.name AS ganador
FROM matches m
JOIN teams t1 ON m.team_a_no = t1.no
JOIN teams t2 ON m.team_b_no = t2.no
JOIN teams winner ON m.winner_team_no = winner.no
WHERE winner.country = 'Colombia'
ORDER BY m.match_date_utc DESC;

-- ============================================================
-- 2. PARTIDOS DONDE COLOMBIA PARTICIPÓ (ganados y perdidos)
-- ============================================================
SELECT 
    m.match_no,
    m.match_date_utc,
    CASE 
        WHEN m.team_a_no = col.no THEN t2.name
        ELSE t1.name
    END AS oponente,
    CASE 
        WHEN m.winner_team_no = col.no THEN 'Ganado'
        ELSE 'Perdido'
    END AS resultado,
    CASE 
        WHEN m.team_a_no = col.no THEN m.team_a_score
        ELSE m.team_b_score
    END AS puntos_colombia,
    CASE 
        WHEN m.team_a_no = col.no THEN m.team_b_score
        ELSE m.team_a_score
    END AS puntos_oponente
FROM matches m
JOIN teams col ON (m.team_a_no = col.no OR m.team_b_no = col.no)
JOIN teams t1 ON m.team_a_no = t1.no
JOIN teams t2 ON m.team_b_no = t2.no
WHERE col.code = 'COL'
ORDER BY m.match_date_utc DESC;

-- ============================================================
-- 3. ESTADÍSTICAS DE COLOMBIA
-- ============================================================
SELECT 
    COUNT(*) AS total_partidos,
    SUM(CASE WHEN m.winner_team_no = col.no THEN 1 ELSE 0 END) AS partidos_ganados,
    SUM(CASE WHEN m.winner_team_no != col.no THEN 1 ELSE 0 END) AS partidos_perdidos,
    ROUND(SUM(CASE WHEN m.winner_team_no = col.no THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS porcentaje_victoria
FROM matches m
JOIN teams col ON (m.team_a_no = col.no OR m.team_b_no = col.no)
WHERE col.code = 'COL';

-- ============================================================
-- 4. PARTIDOS GANADOS POR UN EQUIPO ESPECÍFICO
-- ============================================================
-- Reemplaza 'COL' con el código del equipo deseado
SELECT 
    m.match_no,
    m.match_date_utc,
    t1.name AS equipo_a,
    t2.name AS equipo_b,
    m.team_a_score,
    m.team_b_score,
    m.city,
    m.country
FROM matches m
JOIN teams t1 ON m.team_a_no = t1.no
JOIN teams t2 ON m.team_b_no = t2.no
JOIN teams winner ON m.winner_team_no = winner.no
WHERE winner.code = 'COL'  -- Cambia por el código del equipo
ORDER BY m.match_date_utc DESC;

-- ============================================================
-- 5. DETALLE DE SETS DE UN PARTIDO ESPECÍFICO
-- ============================================================
SELECT 
    m.match_no,
    t1.name AS equipo_a,
    t2.name AS equipo_b,
    s.set_number,
    s.points_team_a,
    s.points_team_b,
    m.team_a_score AS sets_equipo_a,
    m.team_b_score AS sets_equipo_b
FROM matches m
JOIN teams t1 ON m.team_a_no = t1.no
JOIN teams t2 ON m.team_b_no = t2.no
LEFT JOIN sets s ON m.match_no = s.match_no
WHERE m.match_no = 21062  -- Reemplaza con el número del partido
ORDER BY s.set_number;

-- ============================================================
-- 6. PARTIDOS DE UN TORNEO ESPECÍFICO
-- ============================================================
SELECT 
    m.match_no,
    m.match_date_utc,
    t1.name AS equipo_a,
    t2.name AS equipo_b,
    m.team_a_score,
    m.team_b_score,
    winner.name AS ganador
FROM matches m
JOIN teams t1 ON m.team_a_no = t1.no
JOIN teams t2 ON m.team_b_no = t2.no
JOIN teams winner ON m.winner_team_no = winner.no
WHERE m.tournament_no = 1520  -- Men's World Championship 2025
ORDER BY m.match_date_utc;

-- ============================================================
-- 7. PARTIDOS POR POOL/Grupo
-- ============================================================
SELECT 
    p.name AS pool,
    m.match_no,
    m.match_date_utc,
    t1.name AS equipo_a,
    t2.name AS equipo_b,
    m.team_a_score,
    m.team_b_score,
    winner.name AS ganador
FROM matches m
JOIN teams t1 ON m.team_a_no = t1.no
JOIN teams t2 ON m.team_b_no = t2.no
JOIN teams winner ON m.winner_team_no = winner.no
LEFT JOIN pools p ON m.pool_no = p.no
WHERE p.code = 'D'  -- Pool D
ORDER BY m.match_date_utc;

