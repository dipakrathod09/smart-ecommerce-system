--
-- PostgreSQL database dump
--

\restrict owc6eW2mnwJTSfC9cv9CF4zfzNUGpmwaZfu04rzqmV0izo40RbiYMo8TjqYWxDs

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-01-28 10:42:16

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 24577)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    description text,
    price numeric(10,2) NOT NULL,
    stock integer NOT NULL,
    category character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 24576)
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- TOC entry 4981 (class 0 OID 0)
-- Dependencies: 221
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- TOC entry 220 (class 1259 OID 16406)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    password text NOT NULL,
    role character varying(20) DEFAULT 'user'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16405)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4982 (class 0 OID 0)
-- Dependencies: 219
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4817 (class 2604 OID 24580)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 4814 (class 2604 OID 16409)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4975 (class 0 OID 24577)
-- Dependencies: 222
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, name, description, price, stock, category, created_at) FROM stdin;
1	Laptop	14 inch lightweight laptop	55000.00	10	Electronics	2026-01-27 10:38:25.090856
2	Headphones	Noise cancelling headphones	3000.00	25	Electronics	2026-01-27 10:38:25.090856
3	Notebook	A4 size ruled notebook	80.00	100	Stationery	2026-01-27 10:38:25.090856
\.


--
-- TOC entry 4973 (class 0 OID 16406)
-- Dependencies: 220
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, name, email, password, role, created_at) FROM stdin;
2	Rajvi Kholiya	rajvikholiya@gmail.com	scrypt:32768:8:1$0uB5KfAK5QXcSYH1$435a069492ab79efe44c86a214c041c8dc4ad59922c23f8239026e8ed89917f7e99a67eebb7350598f673754f10cf96fdf2655ff97ce3d29d7abc6765ab6e2df	user	2026-01-06 22:28:46.560051
3	Keyan	Keyan@gmail.com	scrypt:32768:8:1$FfANbjXTFRqTxUOt$c5f2c6f25741274e6569b9d1a5aec6c913ac58be14f348e04d3c6281850be1eb3e3f5d4ebf0aa06d3c47a975705bb35340f56a87234525955b81170d42c00e28	user	2026-01-23 11:23:38.865992
1	Dipak Rathod	dipakrathod@gmail.com	scrypt:32768:8:1$CNQnhM1aUfxjmcZX$b66e53cda1d60e45e7aee61b4bb91e86565c343faa09ca0ed4c03ef0f2bb34f1b338130031969500ea1444bb3ff075eb40247e6f477124a9f62b7837e3182c3f	admin	2026-01-06 21:46:21.235496
\.


--
-- TOC entry 4983 (class 0 OID 0)
-- Dependencies: 221
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 3, true);


--
-- TOC entry 4984 (class 0 OID 0)
-- Dependencies: 219
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- TOC entry 4824 (class 2606 OID 24589)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 4820 (class 2606 OID 16421)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4822 (class 2606 OID 16419)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


-- Completed on 2026-01-28 10:42:16

--
-- PostgreSQL database dump complete
--

\unrestrict owc6eW2mnwJTSfC9cv9CF4zfzNUGpmwaZfu04rzqmV0izo40RbiYMo8TjqYWxDs

