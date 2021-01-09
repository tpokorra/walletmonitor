-- password is: DemoDemo
update auth_user set password = 'pbkdf2_sha256$216000$FXCqxdaIG4Dd$QCQEUACd3srB68dlqjekrbHYwThyY3EOQxctr6u0hYQ=', username='demo', email='demo@solidcharity.com' where id='3';
delete from `transaction` where owner_id=3;

insert into `transaction`(crypto_currency, amount_before_fee, amount_after_fee, exchange_rate, fiat_currency, amount, date_valid, owner_id)
values 
('BTC',0.10,0.0990, 754.25,'EUR', 75.42,'2016-12-16 00:00:00.000000',3),
('BTC',0.20,0.199, 555.32,'EUR',150.85,'2016-09-09 00:00:00.000000',3),
('BTC',0.03,0.0299,9988.17,'EUR',299.64,'2020-08-07 00:00:00.000000',3),
('BTC',-0.15,-0.149,14210.97,'EUR',-2131.64,'2018-01-05 00:10:00.000000',3),
('BCH',0.298,0.298,200.00,'EUR',0.0,'2017-01-08 00:00:00.000000',3),
('ETH',0.1,0.099,592.15,'EUR',59.21,'2017-12-29 00:12:00.000000',3),
('ETH',1.0,0.99,100.88,'EUR',100.88,'2019-01-26 00:17:00.000000',3),
('ETH',-0.8,-0.799,638.9,'EUR',-511.12,'2021-01-01 00:34:00.000000',3);
