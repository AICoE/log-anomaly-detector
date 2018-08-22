from trainer import trainer
from infer import infer
import os
import logging

def main():

	model_path = os.environ.get("LADT_MODEL_DIR")
	model = os.environ.get("LADT_MODEL")
	path = model_path+"/"+model


	if os.path.isfile(path) == True:
		logging.info("Models already exist, skipping training")
		infer()


	while True:

		if trainer()  == 1:
			main()
		else:
			pass
		
		infer()


if __name__ == "__main__":
    main()
