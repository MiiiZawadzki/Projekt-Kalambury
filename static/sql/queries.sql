CREATE TABLE public.rooms (
    id integer NOT NULL,
    room_id character varying(16) NOT NULL,
    admin_username text NOT NULL,
    users text[],
    current_word text,
    words text[]
);

CREATE SEQUENCE public.rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

INSERT INTO public.rooms (id, room_id, admin_username, users, current_word, words) VALUES (49, 'H2Sc2V9Ojc4znuvO', 'test', '{test}', 'Koń bez rąk', '{"Koń bez rąk","Koń bez nóg","Żółty ananas","Legia w koronie","Monke in da club"}');
