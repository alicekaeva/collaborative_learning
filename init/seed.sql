-- =============================================================
-- Seed данные для Collaborative Learning (PostgreSQL)
-- Конвертировано из оригинального MySQL дампа
--
-- Все пользователи: пароль = password123
--
-- Пользователи:
--   alisa.alikaeva@gmail.com  — Райнов Гослинг Михайлович    (ADMIN, STUDENT)
--   alikaeva.aa@students.dvfu.ru — Абобус Абоба Абобов        (STUDENT, TEACHER)
--   alikaeva.aa@students.dvfu.com — Аликаева Алиса Андреевна (TEACHER)
--   test@test.com             — Гослинг Райан Петрович        (ADMIN, TEACHER, STUDENT)
--   misha                     — Бураков Алексей Андреевич     (TEACHER)
--   ryan@gosling.com          — Иванов Василий Александрович
--   test1@mail.ru             — Тестовый Тест Тестович
--   alisa.alikaeva@gmail.ru   — Глобусова Екатерина Семеновна
--   ф                         — Андреев Андрей Андреевич      (STUDENT, TEACHER)
-- =============================================================

BEGIN;

-- Порядок важен из-за FK: сначала обнуляем всё
TRUNCATE TABLE
    meetings, tasks, goals,
    messages,
    materials,
    user_favorite_post, post_tag, posts,
    group_student, group_teacher, group_tag, groups,
    admins, teachers, students,
    user_tag,
    tags, categories,
    users
CASCADE;

-- =============================================================
-- CATEGORIES (id сохранены как в оригинале)
-- =============================================================
INSERT INTO categories (id, name) VALUES
    (1, 'Программирование'),
    (2, 'Рисование'),
    (3, 'Биология'),
    (4, 'Тестовая'),
    (5, 'Физика');

-- =============================================================
-- TAGS
-- =============================================================
INSERT INTO tags (id, name, category_id) VALUES
    (1,  'PHP',        1),
    (2,  'Symfony',    1),
    (3,  'Laravel',    1),
    (5,  'Цветы',      2),
    (6,  'python',     1),
    (7,  'Динамика',   5),
    (8,  'Статика',    5),
    (9,  'Квантовая',  5),
    (10, 'Ruby',       1),
    (11, 'C#',         1),
    (12, 'Дома',       2);

-- =============================================================
-- USERS  (пароль для всех: password123)
-- =============================================================
INSERT INTO users (id, email, full_name, password_hash, phone_number, age, alma_mater, points_amount, roles, created_at) VALUES
    (19, 'alisa.alikaeva@gmail.com',        'Райнов Гослинг Михайлович',    '$2b$12$hceUGv3ChPy5Xqr//G5KY.qJuGrXcMN54J7ILhrbbZRp99wu.d9Qm', '89149203600', 24, 'Бакалавриат',                    10,  ARRAY['ROLE_USER','ROLE_ADMIN','ROLE_STUDENT'],           NOW()),
    (20, 'alikaeva.aa@students.dvfu.ru',    'Абобус Абоба Абобов',          '$2b$12$hceUGv3ChPy5Xqr//G5KY.qJuGrXcMN54J7ILhrbbZRp99wu.d9Qm', '89149203699', 21, 'Бакалавриат',                    1010117, ARRAY['ROLE_USER','ROLE_STUDENT','ROLE_TEACHER'],       NOW()),
    (21, 'alisa.alikaeva@gmail.ru',         'Глобусова Екатерина Семеновна','$2b$12$hceUGv3ChPy5Xqr//G5KY.qJuGrXcMN54J7ILhrbbZRp99wu.d9Qm', '89992345600', 21, 'Магистратура',                   0,   ARRAY['ROLE_USER'],                                      NOW()),
    (22, 'alikaeva.aa@students.dvfu.com',   'Аликаева Алиса Андреевна',     '$2b$12$hceUGv3ChPy5Xqr//G5KY.qJuGrXcMN54J7ILhrbbZRp99wu.d9Qm', '89149203699', 21, 'Бакалавриат',                    0,   ARRAY['ROLE_USER','ROLE_TEACHER'],                       NOW()),
    (23, 'ф',                               'Андреев Андрей Андреевич',     '$2b$12$hceUGv3ChPy5Xqr//G5KY.qJuGrXcMN54J7ILhrbbZRp99wu.d9Qm', '89992345694', 1,  'Среднее общее образование',      0,   ARRAY['ROLE_USER','ROLE_STUDENT','ROLE_TEACHER'],        NOW()),
    (24, 'misha',                           'Бураков Алексей Андреевич',    '$2b$12$hceUGv3ChPy5Xqr//G5KY.qJuGrXcMN54J7ILhrbbZRp99wu.d9Qm', '89992345697', 23, 'Бакалавриат',                    0,   ARRAY['ROLE_USER','ROLE_TEACHER'],                       NOW()),
    (25, 'test@test.com',                   'Гослинг Райан Петрович',       '$2b$12$hceUGv3ChPy5Xqr//G5KY.qJuGrXcMN54J7ILhrbbZRp99wu.d9Qm', '89992345698', 22, 'Магистратура',                   0,   ARRAY['ROLE_USER','ROLE_ADMIN','ROLE_TEACHER','ROLE_STUDENT'], NOW()),
    (26, 'test1@mail.ru',                   'Тестовый Тест Тестович',       '$2b$12$hceUGv3ChPy5Xqr//G5KY.qJuGrXcMN54J7ILhrbbZRp99wu.d9Qm', '89992345696', 22, 'Бакалавриат',                    0,   ARRAY['ROLE_USER'],                                      NOW()),
    (27, 'ryan@gosling.com',                'Иванов Василий Александрович', '$2b$12$hceUGv3ChPy5Xqr//G5KY.qJuGrXcMN54J7ILhrbbZRp99wu.d9Qm', '89992345600', 22, 'Среднее профессиональное образование', 0, ARRAY['ROLE_USER'],                                 NOW());

-- user ↔ tag
INSERT INTO user_tag (user_id, tag_id) VALUES
    (19, 1),
    (25, 1);

-- =============================================================
-- ROLE PROFILES
-- =============================================================
INSERT INTO students (id, user_id) VALUES
    (8,  20),
    (9,  25),
    (10, 19),
    (11, 23);

INSERT INTO teachers (id, user_id) VALUES
    (7,  20),
    (8,  25),
    (9,  24),
    (10, 22),
    (11, 23);

INSERT INTO admins (id, user_id) VALUES
    (14, 19),
    (15, 25);

-- =============================================================
-- GROUPS
-- =============================================================
INSERT INTO groups (id, name, info, required_teachers, required_students, administrator_id) VALUES
    (20, 'Учим php',       'Ищем энтузиастов',                                               2, 5,  14),
    (21, 'Учим python',    'Ищем людей, заинтересованных в изучении python',                 3, 6,  15),
    (22, 'Учим си шарп',   'Изучаем .NET',                                                   3, 10, 15);

-- group ↔ tag
INSERT INTO group_tag (group_id, tag_id) VALUES
    (20, 1),
    (20, 2),
    (21, 6),
    (22, 11);

-- group ↔ teacher
INSERT INTO group_teacher (group_id, teacher_id) VALUES
    (20, 8),   -- teacher id=8 → user 25
    (21, 11);  -- teacher id=11 → user 23

-- group ↔ student
INSERT INTO group_student (group_id, student_id) VALUES
    (20, 8),   -- student id=8 → user 20
    (21, 8),
    (21, 10);  -- student id=10 → user 19

-- =============================================================
-- POSTS
-- =============================================================
INSERT INTO posts (id, content, posting_date, author_id) VALUES
    (1,  'Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit...', '2023-04-16 01:55:46', 19),
    (2,  'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam non.',                              '2023-04-16 01:58:48', 19),
    (4,  'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin vel diam at odio aliquam mollis. Vivamus porta mollis lacus quis blandit. Cras dictum nunc id nisi convallis, quis interdum risus luctus.', '2023-04-16 02:01:54', 19),
    (6,  'Duis at aliquet ipsum. Quisque ornare sodales massa id tempus. Quisque sagittis dapibus mauris, at pulvinar nulla fringilla sed. Fusce vitae elit pulvinar, dignissim magna nec, tristique lorem.', '2023-04-16 10:35:28', 22),
    (11, 'Текст рыба',             '2023-04-28 13:50:40', 20),
    (38, 'Лорем ипсум лорем ипсум','2023-05-18 14:40:58', 19),
    (39, 'Тестовый пост',          '2023-05-22 06:03:47', 25);

-- post ↔ tag
INSERT INTO post_tag (post_id, tag_id) VALUES
    (1,  2),
    (2,  2),
    (4,  1),
    (4,  3),
    (6,  3),
    (11, 1),
    (38, 7),
    (38, 9),
    (39, 5),
    (39, 12);

-- post favorites (post_user → user_favorite_post)
INSERT INTO user_favorite_post (user_id, post_id) VALUES
    (19, 11),
    (19, 39);

-- =============================================================
-- MATERIALS
-- =============================================================
INSERT INTO materials (id, name, file_link, mime_type, is_private, creator_group_id, creator_user_id) VALUES
    (7, 'Типы данных php',                  'ATB-Anketa-trudoustrojstvo-646b082bae0cf.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', false, 20, 25),
    (8, 'Органы человека животного тигра',  'Cat03-6466393175620.jpg',                        'image/jpeg',                                                             false, 21, 19);

-- =============================================================
-- MESSAGES
-- =============================================================
INSERT INTO messages (id, content, is_pinned, sending_date, sender_id, receiver_id, receiving_group_id) VALUES
    (97,  'привет',                                                                     false, '2023-04-28 03:52:59', 19, 20,   NULL),
    (98,  'привет',                                                                     false, '2023-04-28 03:53:07', 19, 22,   NULL),
    (99,  'пока',                                                                       false, '2023-04-28 03:53:43', 19, 20,   NULL),
    (100, 'пока',                                                                       false, '2023-04-28 03:55:19', 19, 22,   NULL),
    (101, 'ds',                                                                         false, '2023-05-01 12:19:28', 19, 22,   NULL),
    (102, 'привет',                                                                     false, '2023-05-01 12:19:34', 19, 20,   NULL),
    (103, 'f',                                                                          false, '2023-05-01 12:20:57', 19, 20,   NULL),
    (104, 'f',                                                                          false, '2023-05-01 12:20:58', 19, 20,   NULL),
    (105, 'd',                                                                          false, '2023-05-01 12:20:59', 19, 20,   NULL),
    (106, 'd',                                                                          false, '2023-05-01 12:21:02', 19, 20,   NULL),
    (107, 'd',                                                                          false, '2023-05-01 12:21:04', 19, 20,   NULL),
    (108, 'd',                                                                          false, '2023-05-01 12:21:05', 19, 20,   NULL),
    (109, 'd',                                                                          false, '2023-05-01 12:21:06', 19, 20,   NULL),
    (110, 'd',                                                                          false, '2023-05-01 12:21:07', 19, 20,   NULL),
    (111, 'd',                                                                          false, '2023-05-01 12:21:08', 19, 20,   NULL),
    (112, 'd',                                                                          false, '2023-05-01 12:21:10', 19, 20,   NULL),
    (113, 'e',                                                                          false, '2023-05-01 12:21:11', 19, 20,   NULL),
    (114, 'w',                                                                          false, '2023-05-01 12:21:12', 19, 20,   NULL),
    (115, 'привет',                                                                     false, '2023-05-01 12:21:40', 19, 20,   NULL),
    (117, 'Привет! Я хочу присоединиться к вашей группе test. Можешь добавить меня?',  false, '2023-05-04 01:26:32', 19, 24,   NULL),
    (171, 'Привет! Я хочу присоединиться к вашей группе учим php. Можешь добавить меня?', false, '2023-05-13 06:39:09', 25, 19, NULL),
    (172, 'привет всем!',                                                               true,  '2023-05-13 10:44:31', 19, NULL, 20),
    (173, 'привет',                                                                     false, '2023-05-14 08:06:25', 25, NULL, 21),
    (174, 'привет lf',                                                                  false, '2023-05-16 06:28:59', 19, 25,   NULL),
    (175, 'Привет! Я хочу присоединиться к вашей группе . Можешь добавить меня?',      false, '2023-05-22 06:34:50', 19, 25,   NULL),
    (176, 'Привет! Я хочу присоединиться к вашей группе учимсишарк. Можешь добавить меня?', false, '2023-05-22 06:36:24', 19, 25, NULL),
    (177, 'Привет! Я хочу присоединиться к вашей группе учим си шарк. Можешь добавить меня?', false, '2023-05-22 06:37:12', 19, 25, NULL),
    (178, 'привет!!',                                                                   false, '2023-05-22 09:21:32', 25, NULL, 22),
    (180, 'привет',                                                                     false, '2023-06-05 03:28:00', 25, 19,   NULL),
    (181, 'Привет! Я хочу присоединиться к вашей группе Учим php. Можешь добавить меня?', false, '2023-06-13 04:54:35', 27, 19, NULL),
    (182, 'Привет! Я хочу присоединиться к вашей группе Учим си шарп. Можешь добавить меня?', false, '2023-06-13 06:05:01', 19, 25, NULL),
    (183, 'привет',                                                                     false, '2023-06-13 06:05:18', 19, 22,   NULL),
    (184, 'd',                                                                          false, '2023-06-13 06:06:15', 19, NULL, 20);

-- =============================================================
-- GOALS
-- =============================================================
INSERT INTO goals (id, name, points, deadline, completed, creator_id) VALUES
    (5, 'Выучить php', 100, '2023-05-23', false, 20);

-- =============================================================
-- TASKS
-- =============================================================
INSERT INTO tasks (id, name, link, deadline, points, creator_id) VALUES
    (1, 'Пройти тест по основам php', 'https://symfony.com/doc/current/reference/forms/types/entity.html', '2023-05-15', 10,  20),
    (6, 'эссе',                       NULL,                                                                  '2023-06-30', 100, 20);

-- =============================================================
-- MEETINGS
-- =============================================================
INSERT INTO meetings (id, name, agenda, link, held_on, creator_id) VALUES
    (6, 'Обсуждаем symfony', 'Будем именно знакомиться с этим понятием',
     'http://45.12.237.184:8080/swagger-ui/index.html#/', '2023-06-08 12:58:17', 20);

-- =============================================================
-- Сброс sequence (следующий авто-ID после max существующего)
-- =============================================================
SELECT setval('categories_id_seq',  (SELECT MAX(id) FROM categories));
SELECT setval('tags_id_seq',        (SELECT MAX(id) FROM tags));
SELECT setval('users_id_seq',       (SELECT MAX(id) FROM users));
SELECT setval('students_id_seq',    (SELECT MAX(id) FROM students));
SELECT setval('teachers_id_seq',    (SELECT MAX(id) FROM teachers));
SELECT setval('admins_id_seq',      (SELECT MAX(id) FROM admins));
SELECT setval('groups_id_seq',      (SELECT MAX(id) FROM groups));
SELECT setval('posts_id_seq',       (SELECT MAX(id) FROM posts));
SELECT setval('materials_id_seq',   (SELECT MAX(id) FROM materials));
SELECT setval('messages_id_seq',    (SELECT MAX(id) FROM messages));
SELECT setval('goals_id_seq',       (SELECT MAX(id) FROM goals));
SELECT setval('tasks_id_seq',       (SELECT MAX(id) FROM tasks));
SELECT setval('meetings_id_seq',    (SELECT MAX(id) FROM meetings));

COMMIT;
