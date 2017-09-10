-- Tasks are steps that can be taken to complete a project
create table functraces (
    id          integer primary key autoincrement not null,
    addr        integer,
    arg1        integer,
    arg2        integer,
    arg3        integer
);
