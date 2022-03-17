--  cat createdb.sql| psql -d plei
DROP TABLE accbctx;
CREATE TABLE accbctx (
	id serial PRIMARY KEY,
	platform varchar(20),
	block INT NOT NULL,
	txtime TIMESTAMP NOT NULL,
	txid VARCHAR(80) NOT NULL,
	seq INT NOT NULL,
	txtype VARCHAR(20),
	from_addr VARCHAR(60) NOT NULL,
	to_addr VARCHAR(60) NOT NULL,
	from_human VARCHAR(40),
	to_human VARCHAR(40),
	ccy1 varchar(5) NOT NULL,
	amount1 FLOAT NOT NULL,
	ccy2 varchar(5),
	amount2 FLOAT,
	description VARCHAR(200)

);

DROP TABLE accbctx_raw;
CREATE TABLE accbctx_raw (
	id serial PRIMARY KEY,
	platform varchar(20) NOT NULL,
	txid varchar(80) NOT NULL UNIQUE,
	tx JSONB not NULL
);

grant all on accbctx_raw to pleibackend;
grant all on accbctx to pleibackend;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO pleibackend
