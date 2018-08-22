from trainer import trainer
from infer import infer

def main():

	while True:
		if trainer()  == 1:
			main()
		else:
			pass
		infer()


if __name__ == "__main__":
    main()
