from enum import Enum

class CallbackPrefix(str, Enum):
    DOCTOR_INFO = "doctor_info_"
    SUBSCRIBE = "subscribe_"
    UNSUBSCRIBE = "unsubscribe_"
    VIEW_WEBSITE = "view_website_"
    STATS = "stats_"
    SETTINGS = "settings_"
    TOGGLE_DOCTOR = "toggle_doctor_"

class AdminCallback(str, Enum):
    ADD_DOCTOR = "admin_add_doctor"
    SET_INTERVAL = "admin_set_interval"
    CONFIRM_ADD_DOCTOR = "confirm_add_doctor"
    CANCEL_ADD_DOCTOR = "cancel_add_doctor"
    MANAGE_DOCTORS = "admin_manage_doctors"
    STATS = "admin_stats"
    MANAGE_USERS = "admin_manage_users"
    ACCESS_SETTINGS = "admin_access_settings"
    BACK_TO_ADMIN_PANEL = "back_to_admin_panel"

class MainMenuCallbacks(str, Enum):
    BACK_TO_MAIN = "back_to_main"
    BACK_TO_DOCTORS = "back_to_doctors"
    SUBSCRIPTION_STATS = "subscription_stats"
    NEW_SUBSCRIPTION = "new_subscription"
    REFRESH_STATUS = "refresh_status"
    DETAILED_STATS = "detailed_stats"
    SYSTEM_STATUS = "system_status"
    SHOW_DOCTORS = "show_doctors"
    SHOW_SUBSCRIPTIONS = "show_subscriptions"
    REFRESH_ALL_SUBSCRIPTIONS = "refresh_all_subscriptions"

class ConversationStates(Enum):
    ADD_DOCTOR_LINK = 1
    ADD_DOCTOR_CONFIRM = 2
    SET_CHECK_INTERVAL = 3
