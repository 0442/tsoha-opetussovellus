DROP TABLE exercise_submissions, course_exercises, course_text_materials, course_teachers, course_participants, courses, users CASCADE;

create table users (
    id serial primary key,
    name text unique not null,
    password text not null,
    role integer not null
);

create table courses (
    id serial primary key,
    name text not null,
    description text not null
);

create table course_participants (
    id serial primary key,
    user_id int references users(id) on delete cascade,
    course_id int references courses(id) on delete cascade,
    constraint UC_participant unique (user_id, course_id)
);

create table course_teachers (
    id serial primary key,
    user_id int references users(id) on delete cascade,
    course_id int references courses(id) on delete cascade,
    constraint UC_teacher unique (user_id, course_id)
);

create table course_text_materials (
    id serial primary key,
    course_id int references courses(id) on delete cascade,
    title text not null,
    content text not null
);

create table course_exercises (
    id serial primary key,
    course_id int references courses(id) on delete cascade,
    title text not null,
    question text not null,
    choices text default null,
        -- Null if exercise is answered in plain text.
        -- If not null, exercise is a multiple choice exercise
        -- and should contain a ';' separated list of choices
    correct_answer text not null,
    max_points integer not null
);

create table exercise_submissions (
    id serial primary key,
    exercise_id int references course_exercises(id) on delete cascade,
    user_id int references users(id) on delete cascade,
    answer text,
    constraint UC_submission unique (user_id, exercise_id),
    grade int
);
