toc.dat                                                                                             0000600 0004000 0002000 00000033661 14332722017 0014451 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        PGDMP       )    :        	    
    z            d16ef7la7uufg2     14.5 (Ubuntu 14.5-2.pgdg20.04+2)    14.1 3               0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false                    0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false                    0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false                    1262    2302588    d16ef7la7uufg2    DATABASE     c   CREATE DATABASE d16ef7la7uufg2 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';
    DROP DATABASE d16ef7la7uufg2;
                vtkjqzpzucvlrr    false                    0    0    DATABASE d16ef7la7uufg2    ACL     A   REVOKE CONNECT,TEMPORARY ON DATABASE d16ef7la7uufg2 FROM PUBLIC;
                   vtkjqzpzucvlrr    false    4368                    0    0    d16ef7la7uufg2    DATABASE PROPERTIES     R   ALTER DATABASE d16ef7la7uufg2 SET search_path TO '$user', 'public', 'heroku_ext';
                     vtkjqzpzucvlrr    false                     2615    2302591 
   heroku_ext    SCHEMA        CREATE SCHEMA heroku_ext;
    DROP SCHEMA heroku_ext;
                uc4i6j28gaanuk    false                    0    0    SCHEMA heroku_ext    ACL     4   GRANT USAGE ON SCHEMA heroku_ext TO vtkjqzpzucvlrr;
                   uc4i6j28gaanuk    false    6                    0    0    SCHEMA public    ACL     �   REVOKE ALL ON SCHEMA public FROM postgres;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO vtkjqzpzucvlrr;
GRANT ALL ON SCHEMA public TO PUBLIC;
                   vtkjqzpzucvlrr    false    5                    0    0    LANGUAGE plpgsql    ACL     1   GRANT ALL ON LANGUAGE plpgsql TO vtkjqzpzucvlrr;
                   postgres    false    865         �            1259    5823359    admins    TABLE     W   CREATE TABLE public.admins (
    id bigint,
    unique_id bigint,
    super boolean
);
    DROP TABLE public.admins;
       public         heap    vtkjqzpzucvlrr    false         �            1259    2303263    birthday_donate    TABLE     �   CREATE TABLE public.birthday_donate (
    user_id bigint,
    donater_id bigint,
    donate_sum integer,
    responsible bigint,
    donate_id integer NOT NULL,
    in_process bigint
);
 #   DROP TABLE public.birthday_donate;
       public         heap    vtkjqzpzucvlrr    false         �            1259    2303267    birthday_donate_donate_id_seq    SEQUENCE     �   CREATE SEQUENCE public.birthday_donate_donate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.birthday_donate_donate_id_seq;
       public          vtkjqzpzucvlrr    false    210                    0    0    birthday_donate_donate_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.birthday_donate_donate_id_seq OWNED BY public.birthday_donate.donate_id;
          public          vtkjqzpzucvlrr    false    211         �            1259    2303268    command_all    TABLE        CREATE TABLE public.command_all (
    group_id bigint,
    status boolean,
    initialized_time timestamp without time zone
);
    DROP TABLE public.command_all;
       public         heap    vtkjqzpzucvlrr    false         �            1259    2303271    groups    TABLE     �   CREATE TABLE public.groups (
    id bigint NOT NULL,
    head bigint,
    course integer,
    group_name character varying(40),
    status character varying(20),
    spam_filter boolean DEFAULT false
);
    DROP TABLE public.groups;
       public         heap    vtkjqzpzucvlrr    false         �            1259    5823365    logs    TABLE     �   CREATE TABLE public.logs (
    id integer NOT NULL,
    user_id bigint,
    action character varying(30),
    reason character varying(200),
    date date
);
    DROP TABLE public.logs;
       public         heap    vtkjqzpzucvlrr    false         �            1259    5823364    logs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 "   DROP SEQUENCE public.logs_id_seq;
       public          vtkjqzpzucvlrr    false    221                    0    0    logs_id_seq    SEQUENCE OWNED BY     ;   ALTER SEQUENCE public.logs_id_seq OWNED BY public.logs.id;
          public          vtkjqzpzucvlrr    false    220         �            1259    2303275 	   questions    TABLE     S  CREATE TABLE public.questions (
    question_id integer NOT NULL,
    question character varying(500),
    answer character varying(1000),
    group_id bigint,
    owner_id bigint,
    interesting boolean,
    global boolean,
    read boolean,
    admins_read boolean,
    relates character varying(10) DEFAULT 'all'::character varying
);
    DROP TABLE public.questions;
       public         heap    vtkjqzpzucvlrr    false         �            1259    2303280    questions_question_id_seq    SEQUENCE     �   CREATE SEQUENCE public.questions_question_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.questions_question_id_seq;
       public          vtkjqzpzucvlrr    false    214                    0    0    questions_question_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.questions_question_id_seq OWNED BY public.questions.question_id;
          public          vtkjqzpzucvlrr    false    215         �            1259    9302237    supergroups    TABLE     �   CREATE TABLE public.supergroups (
    id bigint NOT NULL,
    group_name character varying(40),
    status character varying(20),
    spam_filter boolean DEFAULT false,
    manager bigint
);
    DROP TABLE public.supergroups;
       public         heap    vtkjqzpzucvlrr    false         �            1259    2303281    users    TABLE     �   CREATE TABLE public.users (
    id bigint NOT NULL,
    role character varying(20),
    group_id bigint,
    status character varying(10),
    emoji character varying(50),
    birthday date,
    tg_name character varying(50)
);
    DROP TABLE public.users;
       public         heap    vtkjqzpzucvlrr    false         �            1259    2303284    usersingroup    TABLE     i   CREATE TABLE public.usersingroup (
    group_id bigint,
    user_id bigint,
    notifications boolean
);
     DROP TABLE public.usersingroup;
       public         heap    vtkjqzpzucvlrr    false         �            1259    2303287    wish    TABLE     S   CREATE TABLE public.wish (
    user_id bigint,
    wish character varying(1000)
);
    DROP TABLE public.wish;
       public         heap    vtkjqzpzucvlrr    false         ^           2604    2303292    birthday_donate donate_id    DEFAULT     �   ALTER TABLE ONLY public.birthday_donate ALTER COLUMN donate_id SET DEFAULT nextval('public.birthday_donate_donate_id_seq'::regclass);
 H   ALTER TABLE public.birthday_donate ALTER COLUMN donate_id DROP DEFAULT;
       public          vtkjqzpzucvlrr    false    211    210         b           2604    5823368    logs id    DEFAULT     b   ALTER TABLE ONLY public.logs ALTER COLUMN id SET DEFAULT nextval('public.logs_id_seq'::regclass);
 6   ALTER TABLE public.logs ALTER COLUMN id DROP DEFAULT;
       public          vtkjqzpzucvlrr    false    220    221    221         `           2604    2303293    questions question_id    DEFAULT     ~   ALTER TABLE ONLY public.questions ALTER COLUMN question_id SET DEFAULT nextval('public.questions_question_id_seq'::regclass);
 D   ALTER TABLE public.questions ALTER COLUMN question_id DROP DEFAULT;
       public          vtkjqzpzucvlrr    false    215    214                   0    5823359    admins 
   TABLE DATA           6   COPY public.admins (id, unique_id, super) FROM stdin;
    public          vtkjqzpzucvlrr    false    219       4359.dat �          0    2303263    birthday_donate 
   TABLE DATA           n   COPY public.birthday_donate (user_id, donater_id, donate_sum, responsible, donate_id, in_process) FROM stdin;
    public          vtkjqzpzucvlrr    false    210       4350.dat            0    2303268    command_all 
   TABLE DATA           I   COPY public.command_all (group_id, status, initialized_time) FROM stdin;
    public          vtkjqzpzucvlrr    false    212       4352.dat           0    2303271    groups 
   TABLE DATA           S   COPY public.groups (id, head, course, group_name, status, spam_filter) FROM stdin;
    public          vtkjqzpzucvlrr    false    213       4353.dat 	          0    5823365    logs 
   TABLE DATA           A   COPY public.logs (id, user_id, action, reason, date) FROM stdin;
    public          vtkjqzpzucvlrr    false    221       4361.dat           0    2303275 	   questions 
   TABLE DATA           �   COPY public.questions (question_id, question, answer, group_id, owner_id, interesting, global, read, admins_read, relates) FROM stdin;
    public          vtkjqzpzucvlrr    false    214       4354.dat 
          0    9302237    supergroups 
   TABLE DATA           S   COPY public.supergroups (id, group_name, status, spam_filter, manager) FROM stdin;
    public          vtkjqzpzucvlrr    false    222       4362.dat           0    2303281    users 
   TABLE DATA           U   COPY public.users (id, role, group_id, status, emoji, birthday, tg_name) FROM stdin;
    public          vtkjqzpzucvlrr    false    216       4356.dat           0    2303284    usersingroup 
   TABLE DATA           H   COPY public.usersingroup (group_id, user_id, notifications) FROM stdin;
    public          vtkjqzpzucvlrr    false    217       4357.dat           0    2303287    wish 
   TABLE DATA           -   COPY public.wish (user_id, wish) FROM stdin;
    public          vtkjqzpzucvlrr    false    218       4358.dat            0    0    birthday_donate_donate_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.birthday_donate_donate_id_seq', 112, true);
          public          vtkjqzpzucvlrr    false    211                    0    0    logs_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.logs_id_seq', 1, false);
          public          vtkjqzpzucvlrr    false    220                    0    0    questions_question_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.questions_question_id_seq', 57, true);
          public          vtkjqzpzucvlrr    false    215         k           2606    5823363    admins admins_unique_id_key 
   CONSTRAINT     [   ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_unique_id_key UNIQUE (unique_id);
 E   ALTER TABLE ONLY public.admins DROP CONSTRAINT admins_unique_id_key;
       public            vtkjqzpzucvlrr    false    219         e           2606    2303298    groups groups_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.groups DROP CONSTRAINT groups_pkey;
       public            vtkjqzpzucvlrr    false    213         m           2606    5823370    logs logs_pkey 
   CONSTRAINT     L   ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_pkey PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.logs DROP CONSTRAINT logs_pkey;
       public            vtkjqzpzucvlrr    false    221         g           2606    2303300    questions questions_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (question_id);
 B   ALTER TABLE ONLY public.questions DROP CONSTRAINT questions_pkey;
       public            vtkjqzpzucvlrr    false    214         o           2606    9302242    supergroups supergroups_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.supergroups
    ADD CONSTRAINT supergroups_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.supergroups DROP CONSTRAINT supergroups_pkey;
       public            vtkjqzpzucvlrr    false    222         i           2606    2303302    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            vtkjqzpzucvlrr    false    216         p           2606    2303303 !   questions questions_group_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);
 K   ALTER TABLE ONLY public.questions DROP CONSTRAINT questions_group_id_fkey;
       public          vtkjqzpzucvlrr    false    213    214    4197         q           2606    2303308    users users_group_id_fkey    FK CONSTRAINT     z   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);
 C   ALTER TABLE ONLY public.users DROP CONSTRAINT users_group_id_fkey;
       public          vtkjqzpzucvlrr    false    216    213    4197         r           2606    2303318    wish wish_user_id_fkey    FK CONSTRAINT     u   ALTER TABLE ONLY public.wish
    ADD CONSTRAINT wish_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
 @   ALTER TABLE ONLY public.wish DROP CONSTRAINT wish_user_id_fkey;
       public          vtkjqzpzucvlrr    false    4201    216    218                                                                                       4359.dat                                                                                            0000600 0004000 0002000 00000000071 14332722017 0014255 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        347821020	2137	t
426795876	4666	f
2094729373	2049	t
\.


                                                                                                                                                                                                                                                                                                                                                                                                                                                                       4350.dat                                                                                            0000600 0004000 0002000 00000007217 14332722017 0014255 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        408168668	1053851362	0	347821020	19	\N
408168668	428480996	0	347821020	20	\N
408168668	544085464	0	347821020	21	\N
408168668	586541616	0	347821020	23	\N
408168668	571109319	0	347821020	24	\N
408168668	1117423535	0	347821020	25	\N
408168668	896541956	0	347821020	26	\N
408168668	267911469	0	347821020	27	\N
408168668	477470109	0	347821020	28	\N
408168668	543500051	0	347821020	30	\N
408168668	591405020	0	347821020	33	\N
408168668	2094729373	0	347821020	35	\N
408168668	347821020	0	347821020	36	\N
347821020	1053851362	0	408168668	37	\N
347821020	428480996	0	408168668	38	\N
347821020	544085464	0	408168668	39	\N
347821020	852977334	0	408168668	40	\N
347821020	586541616	0	408168668	41	\N
347821020	571109319	0	408168668	42	\N
347821020	1117423535	0	408168668	43	\N
347821020	896541956	0	408168668	44	\N
347821020	267911469	0	408168668	45	\N
347821020	477470109	0	408168668	46	\N
347821020	524014917	0	408168668	47	\N
347821020	543500051	0	408168668	48	\N
347821020	426795876	0	408168668	49	\N
347821020	1257362775	0	408168668	50	\N
347821020	591405020	0	408168668	51	\N
347821020	294085947	0	408168668	52	\N
347821020	2094729373	0	408168668	53	\N
347821020	408168668	0	408168668	54	\N
408168668	852977334	4545	347821020	22	\N
408168668	524014917	1000	347821020	29	\N
408168668	426795876	5000	347821020	31	\N
408168668	1257362775	2555	347821020	32	\N
408168668	294085947	5000	347821020	34	\N
1257362775	428480996	0	347821020	56	\N
1257362775	586541616	0	347821020	57	\N
1257362775	571109319	0	347821020	58	\N
1257362775	591405020	0	347821020	60	\N
1257362775	267911469	0	347821020	63	\N
1257362775	1117423535	0	347821020	65	\N
1257362775	544085464	0	347821020	70	\N
1257362775	852977334	0	347821020	72	\N
540348908	681588169	0	526455934	73	\N
540348908	526455934	0	526455934	74	\N
834318673	540348908	101	526455934	82	101
1230769936	5209658255	0	902019383	83	\N
1230769936	1107756131	0	902019383	84	\N
1230769936	1110227322	0	902019383	85	\N
1230769936	1814366827	0	902019383	86	\N
1230769936	1030109577	0	902019383	87	\N
1230769936	902019383	0	902019383	88	\N
1230769936	939553252	0	902019383	90	\N
1257362775	347821020	1000	347821020	71	1000
1230769936	1244000938	0	902019383	91	\N
1257362775	408168668	1000	347821020	64	1000
1230769936	700839243	0	902019383	92	\N
1257362775	470721643	1000	347821020	69	1000
1230769936	412054237	0	902019383	93	\N
1257362775	477470109	1000	347821020	66	1000
1230769936	671492521	0	902019383	94	\N
1257362775	543500051	1000	347821020	67	1000
1230769936	1795913955	0	902019383	95	\N
1257362775	294085947	2000	347821020	61	2000
1257362775	426795876	0	347821020	59	2000
1230769936	447275066	0	902019383	96	\N
1230769936	2103050192	0	902019383	97	\N
1814366827	5209658255	0	902019383	98	\N
1814366827	1107756131	0	902019383	99	\N
1257362775	896541956	2000	347821020	62	2000
1814366827	1110227322	0	902019383	100	\N
1257362775	1053851362	2000	347821020	55	2000
1257362775	524014917	0	347821020	68	2500
834318673	681588169	0	526455934	75	\N
834318673	526455934	0	526455934	76	\N
834318673	956714113	0	526455934	77	\N
834318673	637909908	0	526455934	78	\N
834318673	463178876	0	526455934	79	\N
834318673	635545570	0	526455934	80	\N
834318673	909604707	0	526455934	81	\N
1814366827	1030109577	0	902019383	101	\N
1814366827	902019383	0	902019383	102	\N
1814366827	417112501	0	902019383	103	\N
1814366827	939553252	0	902019383	104	\N
1814366827	1244000938	0	902019383	105	\N
1814366827	1230769936	0	902019383	106	\N
1814366827	700839243	0	902019383	107	\N
1814366827	412054237	0	902019383	108	\N
1814366827	671492521	0	902019383	109	\N
1814366827	1795913955	0	902019383	110	\N
1814366827	447275066	0	902019383	111	\N
1814366827	2103050192	0	902019383	112	\N
1230769936	417112501	0	902019383	89	750
\.


                                                                                                                                                                                                                                                                                                                                                                                 4352.dat                                                                                            0000600 0004000 0002000 00000000255 14332722017 0014252 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        -1001181672742	t	\N
-661630825	t	\N
-1001372085213	t	\N
-640308986	t	\N
-1001293338350	t	\N
-1001891246816	t	\N
-1001561711179	t	\N
-473948269	t	\N
-1001614404676	t	\N
\.


                                                                                                                                                                                                                                                                                                                                                   4353.dat                                                                                            0000600 0004000 0002000 00000000222 14332722017 0014245 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        -1001614404676	902019383	1	SE-2212	confirmed	f
-1001181672742	347821020	3	CS-2003	confirmed	t
-1001293338350	526455934	3	CS-2006	confirmed	t
\.


                                                                                                                                                                                                                                                                                                                                                                              4361.dat                                                                                            0000600 0004000 0002000 00000000005 14332722017 0014243 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        \.


                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           4354.dat                                                                                            0000600 0004000 0002000 00000012423 14332722017 0014254 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        46	Какие условия по ДР для сайберов?	Темы по разработке/созданию сайтов/приложении и чего угодно не разрешается 🚫 \n\nВыбор тем должен исходить от направления ОП, соответственно сайберам остаётся исследовать методы атак (не обобщенно, а исследовать один вид атак, провести глубокий анализ).\n\n—Будет дополнено—	-1001181672742	347821020	f	\N	t	\N	all
23	Какой номер медсестры медикера?	+7 771 295 5302 Карлыгаш Курманшариповна, медсестра	-1001181672742	347821020	t	t	t	\N	213
55	8.11 уроки будут по расписанию?	Уроков уже не будет	-1001181672742	524014917	\N	\N	t	\N	all
47	в пятницу уроки будут, ведь у школьника  13-14 уроки будут онлайн, у нас что то будут делать?	Уроки будут, отмены нет.	-1001181672742	524014917	\N	\N	t	\N	all
26	Какие условия для получения красного диплома?	Условия для получения КД:\n1. Экзамены гос. предметов (в конце 3 курса) - 90+\n2. Дипломная работа - 90+\n3. Все предметы должны быть 70+\n4. Общий ГПА 3.5+\n5. Ни одного летника	-1001181672742	347821020	t	t	t	\N	all
48	я к тому, что дороги вроде говорят будут перекрывать, хуже чем когда перекрывали из за ремонта	К нам никакой инфы по поводу отмены или перевода уроков на онлайн не сообщалось, так что учёба будет офлайн несмотря на это	-1001181672742	524014917	\N	\N	t	\N	all
49	добрейшего вечерочка, у тебя нету шаблона для заявления для дипломки? пустой шаблон с шабкой и тд	Добрейшей ночи, у меня нет, но я спрошу у других. Глянь на всякий аутлук, кажется туда скидывали шаблон	-1001181672742	524014917	\N	\N	t	\N	all
42	Можешь расписать условие к дипломке с датами?)	Уже расписано, чекай актуальные	-1001181672742	524014917	\N	\N	t	\N	all
57	можешь узнать у cs 01 или 02 в каком формате у них быль файнал по политологии, у них по расписанию будет до нас, заранее спасибо	Ok	-1001181672742	524014917	\N	\N	t	\N	all
43	Чупапи или муняня?	Чупапи Муняня	-1001293338350	540348908	\N	\N	t	\N	all
50	Пабгщищ па?	-	-1001181672742	1053851362	\N	\N	t	\N	all
44	Дай денег	Иди к черту	-1001293338350	540348908	\N	\N	t	\N	all
45	Алимхан, сизде банк карточкасы аркылы толеуге бола ма?	\N	-1001293338350	909604707	\N	\N	f	\N	all
51	Пабгщищ па?	+	-1001181672742	1053851362	\N	\N	t	\N	all
52	где сбор на др ильяса	Это бот начал , время придет тоже начнем	-1001614404676	1244000938	\N	\N	t	\N	all
56	ааа, оказ завтра ендка, кекв	Всмысле, че за эндка??	-1001181672742	524014917	\N	\N	t	\N	all
41	Сводка по собранию	Сводка по собранию\n\nСегодня-завтра скинут гугл док о руководителях с почтой и предложенные темы дипломных работ с возможным описанием к ним\n\nКак закрепить тему за собой?\nДадут форму заявления (тоже сегодня-завтра), где нужны подписи свою/всех участников команды и руководителя\n\nПримерно 2 недели на выбор темы\nЕсли не выберете, то недопуск к защите\n\n1 заявление от себя/команды для выбора темы\n\n1 предзащита (январь-февраль) -> преддипломная практика -> вторая предзащита\n\nЕсли не проходит по предзащите -> недопуск к защите -> приказ на отчисление\n\nЗагружаем в мудл на проверку антиплагиата, только 2 раза можно\n\nОтзыв от научного руководителя и резидента -> выбор даты защиты\n\n3 человека максимум\nЕсли лёгкий проект, то одному можно\n\nС другими ОП не рекомендуется, но можно 1-2 человек\nВ таком случае на защите каждый будет защищаться внутри своих ОП. В случае необходимой подстраховки, можно позвать на защиту.	-1001181672742	347821020	t	t	t	\N	3
\.


                                                                                                                                                                                                                                             4362.dat                                                                                            0000600 0004000 0002000 00000000267 14332722017 0014256 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        -1001773382893	Board Games Club	confirmed	t	347821020
-1001561711179	AITU Chess Club	confirmed	t	347821020
-1001372085213	AITU Gayming: Genshin Impact Club	confirmed	t	347821020
\.


                                                                                                                                                                                                                                                                                                                                         4356.dat                                                                                            0000600 0004000 0002000 00000005676 14332722017 0014272 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        1053851362	student	-1001181672742	active	🌊	2002-06-08	princewths
428480996	student	-1001181672742	active	🔴	2002-05-29	DoctorX
586541616	student	-1001181672742	active	🧿	2003-06-04	Мади
571109319	student	-1001181672742	active	\N	2002-04-26	ඞ
426795876	student	-1001181672742	active	🥵	2002-05-04	Alisher
1257362775	student	-1001181672742	active	👾	2002-10-20	EMPTY
591405020	student	-1001181672742	active	✨	2002-12-13	Alua
294085947	student	-1001181672742	active	🏂	2003-04-13	locked.
896541956	student	-1001181672742	active	🎃	2003-02-12	count
267911469	student	-1001181672742	active	🐉	2002-08-22	Drag
408168668	student	-1001181672742	active	🧔🏾‍♀️	2002-09-05	Dnrv
1117423535	student	-1001181672742	active	🌓	2002-12-18	Фати
477470109	student	-1001181672742	active	🇹🇯	2002-09-01	Rafa
543500051	student	-1001181672742	active	🇿🇦	2002-01-21	Temir
524014917	student	-1001181672742	active	➕	2022-01-17	A
5209658255	student	-1001614404676	active	\N	2004-06-13	Madek🍁
1107756131	student	-1001614404676	active	\N	2005-04-22	Неизвестный
1110227322	student	-1001614404676	active	☺️	2003-05-27	ТИИИЛЬТ
544085464	student	-1001181672742	active	🦋	2003-08-08	Zarina
347821020	head	-1001181672742	active	🤦‍♂️	2003-09-07	Fropzz
852977334	student	-1001181672742	active	😡	2003-01-16	yungdashinobi
681588169	student	-1001293338350	active	✌️	2004-01-11	D.
1814366827	student	-1001614404676	active	\N	2004-11-19	Dreadnout
1030109577	student	-1001614404676	active	\N	2004-08-02	Aigerim🦋🤍
526455934	head	-1001293338350	active	🥵	2001-08-17	alimkhan
956714113	student	-1001293338350	active	🥲	2003-01-23	Darkhan
902019383	head	-1001614404676	active	🤡	2005-08-07	ꀭꀎꌗ꓄ ꍏꋪꌩꌗ
637909908	student	-1001293338350	active	\N	2002-07-13	#A
417112501	student	-1001614404676	active	\N	2003-04-10	Асан
939553252	student	-1001614404676	active	\N	2005-05-20	Ban
1244000938	student	-1001614404676	active	\N	2004-02-03	Zhonchoch
1230769936	student	-1001614404676	active	\N	2005-10-27	~Ida
700839243	student	-1001614404676	active	\N	2004-12-20	Dashokchek
463178876	student	-1001293338350	active	😈	2001-03-30	Эмир
412054237	student	-1001614404676	active	🤠	2004-10-30	ilyas
671492521	student	-1001614404676	active	\N	2004-11-21	жарқынай
834318673	student	-1001293338350	active	\N	2002-10-21	Rassul
811679717	\N	-1001293338350	waiting	\N	\N	Mr_
470721643	student	-1001181672742	active	🇹🇷	2002-05-14	rakniii
447275066	student	-1001614404676	active	\N	2004-05-26	roma
635545570	student	-1001293338350	active	\N	2002-09-24	Дильназ
2103050192	student	-1001614404676	active	\N	2005-06-09	No
909604707	student	-1001293338350	active	👨🏻‍💻	2002-10-29	Rustam
540348908	student	-1001293338350	active	🔞	2222-11-13	zsf
985043349	student	-1001293338350	active	🥷	2002-12-06	Beibarys
1795913955	student	-1001614404676	active	\N	2005-02-15	𝐓𝐚𝐧𝐲𝐚🧝🏻‍♀️🐾
\.


                                                                  4357.dat                                                                                            0000600 0004000 0002000 00000004252 14332722020 0014252 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        -1001293338350	985043349	t
-1001561711179	5209658255	t
-1001561711179	902019383	t
-1001561711179	477470109	t
-1001561711179	347821020	t
-1001614404676	447275066	t
-1001773382893	2094729373	t
-1001293338350	811679717	t
-1001293338350	635545570	t
-1001293338350	463178876	t
-1001293338350	909604707	t
-1001293338350	834318673	t
-1001181672742	267911469	t
-1001891246816	1582515158	t
-1001891246816	347821020	t
-1001614404676	417112501	t
-1001614404676	5209658255	t
-1001614404676	1107756131	t
-1001614404676	1110227322	t
-1001614404676	1814366827	t
-1001614404676	1030109577	t
-1001614404676	902019383	t
-1001614404676	939553252	t
-1001614404676	1244000938	t
-1001614404676	1230769936	t
-1001614404676	700839243	t
-1001614404676	412054237	t
-1001614404676	671492521	t
-1001614404676	1795913955	t
-1001293338350	681588169	t
-1001293338350	526455934	t
-1001293338350	637909908	t
-1001293338350	956714113	t
-1001293338350	540348908	t
-1001181672742	294085947	t
-1001181672742	896541956	t
-1001181672742	408168668	t
-1001181672742	1117423535	t
-1001181672742	477470109	t
-1001181672742	543500051	t
-1001181672742	524014917	t
-1001181672742	470721643	t
-1001181672742	544085464	t
-1001181672742	852977334	t
-661630825	896541956	t
-1001181672742	1053851362	t
-1001181672742	428480996	t
-1001181672742	586541616	t
-1001181672742	571109319	t
-1001181672742	426795876	t
-1001181672742	1257362775	t
-1001181672742	591405020	t
-661630825	267911469	t
-661630825	408168668	t
-661630825	1117423535	t
-1001614404676	2103050192	t
-1001181672742	347821020	t
-1001293963473	347821020	t
-640308986	1053851362	t
-640308986	428480996	t
-640308986	571109319	t
-640308986	426795876	t
-640308986	294085947	t
-640308986	267911469	t
-640308986	1117423535	t
-640308986	347821020	t
-640308986	852977334	t
-473948269	347821020	t
-473948269	294085947	t
-473948269	408168668	t
-661630825	477470109	t
-661630825	543500051	t
-661630825	524014917	t
-661630825	470721643	t
-661630825	544085464	t
-661630825	347821020	t
-661630825	852977334	t
-473948269	477470109	t
-473948269	543500051	t
-473948269	347821020	t
-661630825	1053851362	t
-661630825	586541616	t
-661630825	571109319	t
-661630825	426795876	t
-661630825	591405020	t
-661630825	294085947	t
\.


                                                                                                                                                                                                                                                                                                                                                      4358.dat                                                                                            0000600 0004000 0002000 00000000102 14332722020 0014241 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        540348908	похавать
1814366827	
671492521	
985043349	
\.


                                                                                                                                                                                                                                                                                                                                                                                                                                                              restore.sql                                                                                         0000600 0004000 0002000 00000031067 14332722020 0015366 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        --
-- NOTE:
--
-- File paths need to be edited. Search for $$PATH$$ and
-- replace it with the path to the directory containing
-- the extracted data files.
--
--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5 (Ubuntu 14.5-2.pgdg20.04+2)
-- Dumped by pg_dump version 14.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE d16ef7la7uufg2;
--
-- Name: d16ef7la7uufg2; Type: DATABASE; Schema: -; Owner: vtkjqzpzucvlrr
--

CREATE DATABASE d16ef7la7uufg2 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';


ALTER DATABASE d16ef7la7uufg2 OWNER TO vtkjqzpzucvlrr;

\connect d16ef7la7uufg2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: d16ef7la7uufg2; Type: DATABASE PROPERTIES; Schema: -; Owner: vtkjqzpzucvlrr
--

ALTER DATABASE d16ef7la7uufg2 SET search_path TO '$user', 'public', 'heroku_ext';


\connect d16ef7la7uufg2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: heroku_ext; Type: SCHEMA; Schema: -; Owner: uc4i6j28gaanuk
--

CREATE SCHEMA heroku_ext;


ALTER SCHEMA heroku_ext OWNER TO uc4i6j28gaanuk;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.admins (
    id bigint,
    unique_id bigint,
    super boolean
);


ALTER TABLE public.admins OWNER TO vtkjqzpzucvlrr;

--
-- Name: birthday_donate; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.birthday_donate (
    user_id bigint,
    donater_id bigint,
    donate_sum integer,
    responsible bigint,
    donate_id integer NOT NULL,
    in_process bigint
);


ALTER TABLE public.birthday_donate OWNER TO vtkjqzpzucvlrr;

--
-- Name: birthday_donate_donate_id_seq; Type: SEQUENCE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE SEQUENCE public.birthday_donate_donate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.birthday_donate_donate_id_seq OWNER TO vtkjqzpzucvlrr;

--
-- Name: birthday_donate_donate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER SEQUENCE public.birthday_donate_donate_id_seq OWNED BY public.birthday_donate.donate_id;


--
-- Name: command_all; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.command_all (
    group_id bigint,
    status boolean,
    initialized_time timestamp without time zone
);


ALTER TABLE public.command_all OWNER TO vtkjqzpzucvlrr;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.groups (
    id bigint NOT NULL,
    head bigint,
    course integer,
    group_name character varying(40),
    status character varying(20),
    spam_filter boolean DEFAULT false
);


ALTER TABLE public.groups OWNER TO vtkjqzpzucvlrr;

--
-- Name: logs; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.logs (
    id integer NOT NULL,
    user_id bigint,
    action character varying(30),
    reason character varying(200),
    date date
);


ALTER TABLE public.logs OWNER TO vtkjqzpzucvlrr;

--
-- Name: logs_id_seq; Type: SEQUENCE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE SEQUENCE public.logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.logs_id_seq OWNER TO vtkjqzpzucvlrr;

--
-- Name: logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER SEQUENCE public.logs_id_seq OWNED BY public.logs.id;


--
-- Name: questions; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.questions (
    question_id integer NOT NULL,
    question character varying(500),
    answer character varying(1000),
    group_id bigint,
    owner_id bigint,
    interesting boolean,
    global boolean,
    read boolean,
    admins_read boolean,
    relates character varying(10) DEFAULT 'all'::character varying
);


ALTER TABLE public.questions OWNER TO vtkjqzpzucvlrr;

--
-- Name: questions_question_id_seq; Type: SEQUENCE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE SEQUENCE public.questions_question_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.questions_question_id_seq OWNER TO vtkjqzpzucvlrr;

--
-- Name: questions_question_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER SEQUENCE public.questions_question_id_seq OWNED BY public.questions.question_id;


--
-- Name: supergroups; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.supergroups (
    id bigint NOT NULL,
    group_name character varying(40),
    status character varying(20),
    spam_filter boolean DEFAULT false,
    manager bigint
);


ALTER TABLE public.supergroups OWNER TO vtkjqzpzucvlrr;

--
-- Name: users; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    role character varying(20),
    group_id bigint,
    status character varying(10),
    emoji character varying(50),
    birthday date,
    tg_name character varying(50)
);


ALTER TABLE public.users OWNER TO vtkjqzpzucvlrr;

--
-- Name: usersingroup; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.usersingroup (
    group_id bigint,
    user_id bigint,
    notifications boolean
);


ALTER TABLE public.usersingroup OWNER TO vtkjqzpzucvlrr;

--
-- Name: wish; Type: TABLE; Schema: public; Owner: vtkjqzpzucvlrr
--

CREATE TABLE public.wish (
    user_id bigint,
    wish character varying(1000)
);


ALTER TABLE public.wish OWNER TO vtkjqzpzucvlrr;

--
-- Name: birthday_donate donate_id; Type: DEFAULT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.birthday_donate ALTER COLUMN donate_id SET DEFAULT nextval('public.birthday_donate_donate_id_seq'::regclass);


--
-- Name: logs id; Type: DEFAULT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.logs ALTER COLUMN id SET DEFAULT nextval('public.logs_id_seq'::regclass);


--
-- Name: questions question_id; Type: DEFAULT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.questions ALTER COLUMN question_id SET DEFAULT nextval('public.questions_question_id_seq'::regclass);


--
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.admins (id, unique_id, super) FROM stdin;
\.
COPY public.admins (id, unique_id, super) FROM '$$PATH$$/4359.dat';

--
-- Data for Name: birthday_donate; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.birthday_donate (user_id, donater_id, donate_sum, responsible, donate_id, in_process) FROM stdin;
\.
COPY public.birthday_donate (user_id, donater_id, donate_sum, responsible, donate_id, in_process) FROM '$$PATH$$/4350.dat';

--
-- Data for Name: command_all; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.command_all (group_id, status, initialized_time) FROM stdin;
\.
COPY public.command_all (group_id, status, initialized_time) FROM '$$PATH$$/4352.dat';

--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.groups (id, head, course, group_name, status, spam_filter) FROM stdin;
\.
COPY public.groups (id, head, course, group_name, status, spam_filter) FROM '$$PATH$$/4353.dat';

--
-- Data for Name: logs; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.logs (id, user_id, action, reason, date) FROM stdin;
\.
COPY public.logs (id, user_id, action, reason, date) FROM '$$PATH$$/4361.dat';

--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.questions (question_id, question, answer, group_id, owner_id, interesting, global, read, admins_read, relates) FROM stdin;
\.
COPY public.questions (question_id, question, answer, group_id, owner_id, interesting, global, read, admins_read, relates) FROM '$$PATH$$/4354.dat';

--
-- Data for Name: supergroups; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.supergroups (id, group_name, status, spam_filter, manager) FROM stdin;
\.
COPY public.supergroups (id, group_name, status, spam_filter, manager) FROM '$$PATH$$/4362.dat';

--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.users (id, role, group_id, status, emoji, birthday, tg_name) FROM stdin;
\.
COPY public.users (id, role, group_id, status, emoji, birthday, tg_name) FROM '$$PATH$$/4356.dat';

--
-- Data for Name: usersingroup; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.usersingroup (group_id, user_id, notifications) FROM stdin;
\.
COPY public.usersingroup (group_id, user_id, notifications) FROM '$$PATH$$/4357.dat';

--
-- Data for Name: wish; Type: TABLE DATA; Schema: public; Owner: vtkjqzpzucvlrr
--

COPY public.wish (user_id, wish) FROM stdin;
\.
COPY public.wish (user_id, wish) FROM '$$PATH$$/4358.dat';

--
-- Name: birthday_donate_donate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vtkjqzpzucvlrr
--

SELECT pg_catalog.setval('public.birthday_donate_donate_id_seq', 112, true);


--
-- Name: logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vtkjqzpzucvlrr
--

SELECT pg_catalog.setval('public.logs_id_seq', 1, false);


--
-- Name: questions_question_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vtkjqzpzucvlrr
--

SELECT pg_catalog.setval('public.questions_question_id_seq', 57, true);


--
-- Name: admins admins_unique_id_key; Type: CONSTRAINT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_unique_id_key UNIQUE (unique_id);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: logs logs_pkey; Type: CONSTRAINT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_pkey PRIMARY KEY (id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (question_id);


--
-- Name: supergroups supergroups_pkey; Type: CONSTRAINT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.supergroups
    ADD CONSTRAINT supergroups_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: questions questions_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: users users_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: wish wish_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vtkjqzpzucvlrr
--

ALTER TABLE ONLY public.wish
    ADD CONSTRAINT wish_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: DATABASE d16ef7la7uufg2; Type: ACL; Schema: -; Owner: vtkjqzpzucvlrr
--

REVOKE CONNECT,TEMPORARY ON DATABASE d16ef7la7uufg2 FROM PUBLIC;


--
-- Name: SCHEMA heroku_ext; Type: ACL; Schema: -; Owner: uc4i6j28gaanuk
--

GRANT USAGE ON SCHEMA heroku_ext TO vtkjqzpzucvlrr;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: vtkjqzpzucvlrr
--

REVOKE ALL ON SCHEMA public FROM postgres;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO vtkjqzpzucvlrr;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: LANGUAGE plpgsql; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON LANGUAGE plpgsql TO vtkjqzpzucvlrr;


--
-- PostgreSQL database dump complete
--

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         