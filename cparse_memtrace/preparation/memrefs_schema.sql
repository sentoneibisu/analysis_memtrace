-- Tasks are steps that can be taken to complete a project
create table memrefs (
    id          integer primary key autoincrement not null,
    pc          integer,
    write       integer,
    size        integer,
    addr        integer,
    mem_data    integer
);
