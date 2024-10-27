from ml.classificators.swear_classifier import load_swear_model
from ml.classificators.toxic_classifier import load_toxic_model
from ml.constants import TOXIC_CLF_PATH

swear_clf = load_swear_model()

toxic_clf = load_toxic_model(TOXIC_CLF_PATH)
