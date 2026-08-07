.PHONY: doctor update backup restore deploy release docs logs

doctor:
	cbos doctor

update:
	cbos update

backup:
	cbos backup

restore:
	cbos restore

deploy:
	cbos deploy

release:
	cbos release

docs:
	cbos docs

logs:
	cbos logs
