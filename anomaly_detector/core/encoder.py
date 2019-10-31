"""Encoder class for converting raw log to vector representation."""
import os
import logging
from anomaly_detector.model import W2VModel
from anomaly_detector.exception import ModelSaveException, ModelLoadException


class LogEncoderCatalog(object):
    """Log Encoder Catalog class to provide a point of extension for new encoding schemas."""

    def __init__(self, encoder_api, config, recreate_model=False):
        """Initialize the encoder to allow for training model which converts raw logs to vector for ML.

        :param encoder_api: select which encoding scheme to use for nlp of logs
        :param config: configuration for the application
        :param recreate_model: when set to true will recreate the model
        """
        self.config = config
        self.update_model = os.path.isfile(self.config.W2V_MODEL_PATH) and self.config.TRAIN_UPDATE_MODEL
        self.recreate_model = recreate_model
        if encoder_api in self._instance_method_choices:
            self.encoder_api = encoder_api
        else:
            raise ValueError("Invalid Value for Param: {0}".format(encoder_api))

    def encode_log(self, dataframe):
        """Encode logs using data frame provided from input data source.

        :param dataframe: This is a pandas data frame that has been cleaned before being processed by this model.
        :return: None
        """
        if dataframe is not None:
            if not self.recreate_model:
                self.model.update(dataframe)
            else:
                self.model.create(dataframe,
                                  self.config.TRAIN_VECTOR_LENGTH,
                                  self.config.TRAIN_WINDOW)
            try:
                self.model.save(self.config.W2V_MODEL_PATH)
            except ModelSaveException as ex:
                logging.error("Failed to save W2V model: %s" % ex)
                raise

    def _w2v_encoder(self):
        """Load the encoder and prepare model for processing logs.

        :return: None
        """
        self.model = W2VModel(config=self.config)
        try:
            self.model.load(self.config.W2V_MODEL_PATH)
        except ModelLoadException as ex:
            logging.error("Failed to load W2V model: %s" % ex)
            raise

        return self.model

    def one_vector(self, data):
        """Based on the data you provide you will get the vector representation of that log message.

        :param data: log message to encoded.
        :return: Vector object of the encoded log.
        """
        return self.model.one_vector(data)

    _instance_method_choices = {'w2v_encoder': _w2v_encoder}

    def build(self):
        """Build encoder based on which class encoding scheme you select in the constructor.

        :return:None
        """
        return self._instance_method_choices[self.encoder_api].__get__(self)()
