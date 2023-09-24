DROP TABLE course_exercises, course_text_materials, course_teachers, course_participants, courses, users CASCADE;

CREATE TABLE users (
    id serial primary key,
    name text unique,
    password text,
    role integer
);

CREATE TABLE courses (
    id serial primary key,
    name text,
    description text
);

CREATE TABLE course_participants (
    id serial primary key,
    user_id int references users(id) ON DELETE CASCADE,
    course_id int references courses(id) ON DELETE CASCADE,
    CONSTRAINT UC_participant UNIQUE (user_id, course_id)
);

CREATE TABLE course_teachers (
    id serial primary key,
    user_id int references users(id) ON DELETE CASCADE,
    course_id int references courses(id) ON DELETE CASCADE,
    CONSTRAINT UC_teacher UNIQUE (user_id, course_id)
);

CREATE TABLE course_text_materials (
    id serial primary key,
    course_id int references courses(id) ON DELETE CASCADE,
    title text,
    content text
);

CREATE TABLE course_exercises (
    id serial primary key,
    course_id int references courses(id) ON DELETE CASCADE,
    title text,
    question text,
    correct_answer text
);

CREATE TABLE exercise_submissions (
    id serial primary key,
    exercise_id int references course_exercises(id),
    user_id int references users(id) ON DELETE CASCADE,
    answer text,
    CONSTRAINT UC_submission UNIQUE (user_id, exercise_id)
);