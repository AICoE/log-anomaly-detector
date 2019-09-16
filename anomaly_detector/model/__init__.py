"""Model package."""
from anomaly_detector.model.base_model import BaseModel
from anomaly_detector.model.som_model import SOMModel
from anomaly_detector.model.sompy_model import SOMPYModel
from anomaly_detector.model.w2v_model import W2VModel

__all__ = ['BaseModel',
           'SOMModel',
           'SOMPYModel',
           'W2VModel']
