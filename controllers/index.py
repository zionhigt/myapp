from controllers.users import users_ctrl
from controllers.data import data_ctrl
def init(api):
    users_ctrl(api)
    data_ctrl(api)