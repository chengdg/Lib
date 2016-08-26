# -*- coding: utf-8 -*-

__author__ = 'bert'

WEIXIN_API_PROTOCAL = 'https'
WEIXIN_API_DOMAIN = 'api.weixin.qq.com'


API_GET= 'get'
API_POST= 'post'

API_CLASSES = {
	'get_user_info': 'eaglet.core.wxapi.api_get_user_info.WeixinUserApi',
	'create_qrcode_ticket': 'eaglet.core.wxapi.api_create_qrcode_ticket.WeixinCreateQrcodeTicketApi',
	'get_qrcode': 'eaglet.core.wxapi.api_get_qrcode.WexinGetQrcodeApi',
	'create_customerized_menu': 'eaglet.core.wxapi.api_customerized_menu.WeixinCreateCustomerizedMenuApi',
	'delete_customerized_menu': 'eaglet.core.wxapi.api_customerized_menu.WeixinDeleteCustomerizedMenuApi',
	'get_customerized_menu': 'eaglet.core.wxapi.api_customerized_menu.WeixinGetCustomerizedMenuApi',
	'get_groups': 'eaglet.core.wxapi.api_get_groups.WeixinGroupsApi',
	'send_custom_msg': 'eaglet.core.wxapi.api_send_custom_msg.WeixinSendCustomMsgApi',
	'get_member_group_id': 'eaglet.core.wxapi.api_get_member_groupid.WeixinGetMemberGroupIdApi',
	'upload_media_image': 'eaglet.core.wxapi.api_upload_media.WeixinUploadMediaImageApi',
	'upload_content_media_image': 'eaglet.core.wxapi.api_upload_media.WeixinUploadContentMediaImageApi',
	'upload_media_voice': 'eaglet.core.wxapi.api_upload_media.WeixinUploadMediaVoiceApi',
	'upload_media_news': 'eaglet.core.wxapi.api_upload_news.WeixinUploadNewsApi',
	'send_mass_message': 'eaglet.core.wxapi.api_send_mass_message.WeixinMassSendApi',
	'create_deliverynotify': 'eaglet.core.wxapi.api_pay_delivernotify.WeixinPayDeliverNotifyApi',
	'send_template_message': 'eaglet.core.wxapi.api_send_template_message.WeixinTemplateMessageSendApi',
	'delete_mass_message': 'eaglet.core.wxapi.api_delete_mass_message.WeixinDeleteMassMessageApi',
	'get_component_token': 'eaglet.core.wxapi.api_component_token.WeixinComponentToken',
	'api_create_preauthcode': 'eaglet.core.wxapi.api_create_preauthcode.WeixinCreatePreauthcode',
	'api_query_auth': 'eaglet.core.wxapi.api_query_auth.WeixinQueryAuth',
	'api_authorizer_token': 'eaglet.core.wxapi.api_authorizer_token.WeixinGetAuthorizerToken',
	'api_get_authorizer_info': 'eaglet.core.wxapi.api_get_authorizer_info.WeixinGetAuthorizerInfo',
	'api_shakearound_device_aopplyid':'eaglet.core.wxapi.api_shakearound_device_applyid.WeixinShakeAroundDeviceApplyid',
	'api_get_user_summary':'eaglet.core.wxapi.api_get_user_analysis.WeixinGetUserSummaryApi',
	'api_get_user_cumulate':'eaglet.core.wxapi.api_get_user_analysis.WeixinGetUserCumulateApi',
	}