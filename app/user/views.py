import json
import os
from datetime import datetime
from utils.views import get_current_year
import jwt
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import (DjangoUnicodeDecodeError, smart_bytes,
																	 smart_str)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import (filters, generics, permissions, status, views,
														viewsets)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .models import User
from .renderers import UserRenderer
from .serializers import *

# Create your views here.

class RegisterView(generics.GenericAPIView):

	permission_classes = [AllowAny]
	serializer_class = RegisterSerializer
	renderer_classes = (UserRenderer,)
	throttle_classes = [AnonRateThrottle]

	def post(self, request):

		user = request.data
		try:

				user = User.objects.get(phone_number=user['phone_number'])
			
				return Response({'error_type': "IntegrityError", 'error': "User already exists",
															'status_code': 400
															}, status=400)
		except User.DoesNotExist:
				pass
				# print("Does not exist")

		serializer = self.serializer_class(data=user)
		serializer.is_valid(raise_exception=True)

		try:
			serializer.save()
		except IntegrityError as e:
	
			errorMessage = str(e.__cause__).split("DETAIL: ")[1]

			key = errorMessage.split("=")[0]
			key = key.replace("Key", "")
			key = key.replace("(", "")
			key = key.replace(")", "")
			key = key.replace("_", " ")

			key = key.strip()
			key = key.capitalize()

			mainMessage = errorMessage.split("=")[1]

			mainMessage = mainMessage.split(")")[1]

			mainMessage = mainMessage.replace("\n", "")

			return Response({'error_type': "IntegrityError", 'error': key+mainMessage,
												'status_code': 400
												}, status=400)

		password = serializer.validated_data['password']
		user_data = serializer.data
		user = User.objects.get(phone_number=user_data['phone_number'])

		user.is_verified = True
		user.save()

		if user:
			jsonData = serializer.data
			data_set = {"id": user.id, "email": user.email, "full_name": user.full_name,
									"phone_number": user.phone_number, "is_staff": user.is_staff}
			json_dump = json.dumps(data_set)
			json_object = json.loads(json_dump)
			return Response(json_object, status=status.HTTP_201_CREATED)
		
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
	
	permission_classes = [AllowAny]
	serializer_class = LoginSerializer
	renderer_classes = (UserRenderer,)

	throttle_classes = [AnonRateThrottle]

	
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
class RequestPasswordResetEmail(generics.GenericAPIView):
		serializer_class = ResetPasswordEmailRequestSerializer
		permission_classes = [AllowAny]
		throttle_classes = [AnonRateThrottle]

		def post(self, request):
				serializer = self.serializer_class(data=request.data)

				current_year_string = str(get_current_year())

				email = request.data.get('email', '')
				phone_number = request.data.get('phone_number', '')
				
				print("Email", email)
				print("phoneNumber", phone_number)
				formatted_phone_number = phone_number
				# check if the email exist if so 
				if email:
					if User.objects.filter(email=email).exists():
							user = User.objects.get(email=email)
							uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
							token = PasswordResetTokenGenerator().make_token(user)
							current_site = get_current_site(
									request=request).domain
							relativeLink = reverse(
									'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

							redirect_url = "https://tig.citam.org/admin/#/change-password/"
							# redirect_url = request.data.get('redirect_url', '')
							absurl = 'https://'+current_site + relativeLink
							# absurl = 'http://'+current_site + relativeLink

							reset_url = absurl+"?redirect_url="+redirect_url

							# email_body = 'Hello, \n Use link below to reset your password  \n' + \
							#     absurl+"?redirect_url="+redirect_url
							email_body = """ \
											<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
												<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
												<head>
												<!--[if gte mso 9]>
												<xml>
													<o:OfficeDocumentSettings>
														<o:AllowPNG/>
														<o:PixelsPerInch>96</o:PixelsPerInch>
													</o:OfficeDocumentSettings>
												</xml>
												<![endif]-->
													<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
													<meta name="viewport" content="width=device-width, initial-scale=1.0">
													<meta name="x-apple-disable-message-reformatting">
													<!--[if !mso]><!--><meta http-equiv="X-UA-Compatible" content="IE=edge"><!--<![endif]-->
													<title></title>

														<style type="text/css">
															@media only screen and (min-width: 620px) {
													.u-row {
														width: 600px !important;
													}
													.u-row .u-col {
														vertical-align: top;
													}

													.u-row .u-col-100 {
														width: 600px !important;
													}

												}

												@media (max-width: 620px) {
													.u-row-container {
														max-width: 100% !important;
														padding-left: 0px !important;
														padding-right: 0px !important;
													}
													.u-row .u-col {
														min-width: 320px !important;
														max-width: 100% !important;
														display: block !important;
													}
													.u-row {
														width: calc(100% - 40px) !important;
													}
													.u-col {
														width: 100% !important;
													}
													.u-col > div {
														margin: 0 auto;
													}
												}
												body {
													margin: 0;
													padding: 0;
												}

												table,
												tr,
												td {
													vertical-align: top;
													border-collapse: collapse;
												}

												p {
													margin: 0;
												}

												.ie-container table,
												.mso-container table {
													table-layout: fixed;
												}

												* {
													line-height: inherit;
												}

												a[x-apple-data-detectors='true'] {
													color: inherit !important;
													text-decoration: none !important;
												}

												table, td { color: #000000; } a { color: #0000ee; text-decoration: underline; } @media (max-width: 480px) { #u_content_image_1 .v-src-width { width: auto !important; } #u_content_image_1 .v-src-max-width { max-width: 40% !important; } #u_content_heading_1 .v-font-size { font-size: 38px !important; } #u_content_image_3 .v-src-width { width: 100% !important; } #u_content_image_3 .v-src-max-width { max-width: 100% !important; } #u_content_text_5 .v-container-padding-padding { padding: 10px 30px 11px 10px !important; } }
														</style>



												<!--[if !mso]><!--><link href="https://fonts.googleapis.com/css?family=Calibri:400,700&display=swap" rel="stylesheet" type="text/css"><!--<![endif]-->

												</head>

												<body class="clean-body u_body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #F5F5F5;color: #000000">
													<!--[if IE]><div class="ie-container"><![endif]-->
													<!--[if mso]><div class="mso-container"><![endif]-->
													<table style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #F5F5F5;width:100%" cellpadding="0" cellspacing="0">
													<tbody>
													<tr style="vertical-align: top">
														<td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
														<!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color: #F5F5F5;"><![endif]-->


												<div class="u-row-container" style="padding: 0px;background-color: transparent">
													<div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #f1f2f6;">
														<div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
															<!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #f1f2f6;"><![endif]-->

												<!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
												<div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
													<div style="width: 100% !important;">
													<!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;"><!--<![endif]-->

												<table  style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:30px 10px 31px;font-family:'Calibri',sans-serif;" align="left">

												<table width="100%" cellpadding="0" cellspacing="0" border="0">
													<tr>
														<td style="padding-right: 0px;padding-left: 0px;" align="center">

															<img align="center" border="0" src="https://jumuisha.net/media/jumuisha.png" alt="Email" title="Email" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: inline-block !important;border: none;height: auto;float: none;width: 55%;max-width: 96px;" width="96" class="v-src-width v-src-max-width"/>

														</td>
													</tr>
												</table>

															</td>
														</tr>
													</tbody>
												</table>

													<!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
													</div>
												</div>
												<!--[if (mso)|(IE)]></td><![endif]-->
															<!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
														</div>
													</div>
												</div>



												<div class="u-row-container" style="padding: 0px;background-color: transparent">
													<div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #fbfcff;">
														<div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
															<!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #fbfcff;"><![endif]-->

												<!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
												<div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
													<div style="width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
													<!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

												<table id="u_content_heading_1" style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:50px 10px 30px;font-family:'Calibri',sans-serif;" align="left">

													<h1 class="v-font-size" style="margin: 0px; color: #373D57; line-height: 140%; text-align: center; word-wrap: break-word; font-weight: normal; font-family: 'Calibri','Calibri',sans-serif; font-size: 36px;">
														<strong>Reset Password</strong>
													</h1>

															</td>
														</tr>
													</tbody>
												</table>

												<table id="" style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:15px 10px 40px;font-family:'Calibri',sans-serif;" align="left">

												<table width="100%" cellpadding="0" cellspacing="0" border="0">
													<tr>
														<td style="padding-right: 0px;padding-left: 0px;" align="center">

															<img align="center" border="0" src="https://jumuisha.net/media/rotation-lock.png" alt="Reset" title="Reset" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: inline-block !important;border: none;height: auto;float: none;width: 55%;max-width: 96px;" width="96" class="v-src-width v-src-max-width"/>

														</td>
													</tr>
												</table>

															</td>
														</tr>
													</tbody>
												</table>

													<!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
													</div>
												</div>
												<!--[if (mso)|(IE)]></td><![endif]-->
															<!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
														</div>
													</div>
												</div>

												<div class="u-row-container" style="padding: 0px;background-color: transparent">
													<div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #ffffff;">
														<div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
															<!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #ffffff;"><![endif]-->

												<!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
												<div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
													<div style="width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
													<!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

												<table id="u_content_text_5" style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:40px 30px 20px 40px;font-family:'Calibri',sans-serif;" align="left">

													<div style="color: #4b4a4a; line-height: 190%; text-align: left; word-wrap: break-word;">
														<p style="font-size: 14px; line-height: 190%;"><span style="font-size: 18px; line-height: 34.2px; font-family: Calibri, sans-serif;"><strong><span style="line-height: 34.2px; font-size: 18px;">Hello <span style="text-transform: capitalize">"""+user.full_name+"""</span>,</span></strong></span></p>
												<p style="font-size: 14px; line-height: 190%;">Use the link below to set up a new password for your account.</p>
												<p style="font-size: 14px; line-height: 190%;">Please ignore this email if you did not make the request.</p>
													</div>

															</td>
														</tr>
													</tbody>
												</table>

													<!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
													</div>
												</div>
												<!--[if (mso)|(IE)]></td><![endif]-->
															<!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
														</div>
													</div>
												</div>



												<div class="u-row-container" style="padding: 0px;background-color: transparent">
													<div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #ffffff;">
														<div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
															<!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #ffffff;"><![endif]-->

												<!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
												<div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
													<div style="width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
													<!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

												<table style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:15px 10px 30px;font-family:'Calibri',sans-serif;" align="left">

												<div align="center">
													<!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;font-family:'Calibri',sans-serif;"><tr><td style="font-family:'Calibri',sans-serif;" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://unlayer.com" style="height:49px; v-text-anchor:middle; width:249px;" arcsize="0%" stroke="f" fillcolor="#62D6A5"><w:anchorlock/><center style="color:#FFFFFF;font-family:'Calibri',sans-serif;"><![endif]-->
														<a href="""+reset_url+""" target="_blank" style="box-sizing: border-box;display: inline-block;font-family:'Calibri',sans-serif;text-decoration: none;-webkit-text-size-adjust: none;text-align: center;color: #FFFFFF; background-color: #62D6A5; border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px; width:auto; max-width:100%; overflow-wrap: break-word; word-break: break-word; word-wrap:break-word; mso-border-alt: none;">
															<span style="display:block;padding:16px 50px;line-height:120%;"><strong><span style="font-size: 14px; line-height: 16.8px;">Click TO Reset Your Password</span></strong></span>
														</a>
													<!--[if mso]></center></v:roundrect></td></tr></table><![endif]-->
												</div>

															</td>
														</tr>
													</tbody>
												</table>

													<!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
													</div>
												</div>
												<!--[if (mso)|(IE)]></td><![endif]-->
															<!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
														</div>
													</div>
												</div>



												<div class="u-row-container" style="padding: 0px;background-color: transparent">
													<div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #fbfcff;">
														<div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
															<!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #fbfcff;"><![endif]-->

												<!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
												<div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
													<div style="width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
													<!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

												<table style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:57px 10px 20px;font-family:'Calibri',sans-serif;" align="left">

												<div align="center">
													<div style="display: table; max-width:143px;">
													<!--[if (mso)|(IE)]><table width="143" cellpadding="0" cellspacing="0" border="0"><tr><td style="border-collapse:collapse;" align="center"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse; mso-table-lspace: 0pt;mso-table-rspace: 0pt; width:143px;"><tr><![endif]-->


														<!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 16px;" valign="top"><![endif]-->
														<table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 16px">
															<tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
																<a href="https://web.facebook.com/Jumuisha-107242448304663" title="Facebook" target="_blank">
																	<img src="https://jumuisha.net/media/facebook.png" alt="Facebook" title="Facebook" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
																</a>
															</td></tr>
														</tbody></table>
														<!--[if (mso)|(IE)]></td><![endif]-->

														<!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 16px;" valign="top"><![endif]-->
														<table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 16px">
															<tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
																<a href="https://twitter.com/JumuishaT" title="Twitter" target="_blank">
																	<img src="https://jumuisha.net/media/twitter.png" alt="Twitter" title="Twitter" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
																</a>
															</td></tr>
														</tbody></table>
														<!--[if (mso)|(IE)]></td><![endif]-->

														<!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 0px;" valign="top"><![endif]-->
														<table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 0px">
															<tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
																<a href="https://www.linkedin.com/company/jumuisha" title="LinkedIn" target="_blank">
																	<img src="https://jumuisha.net/media/linkedin.png" alt="LinkedIn" title="LinkedIn" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
																</a>
															</td></tr>
														</tbody></table>
														<!--[if (mso)|(IE)]></td><![endif]-->

														<!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 0px;" valign="top"><![endif]-->
														<table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 0px">
															<tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
																<a href="https://www.youtube.com/channel/UC2Wu_v_bGR4eW9PCc_F6Pqg" title="Youtube" target="_blank">
																	<img src="https://jumuisha.net/media/youtube.png" alt="Youtube" title="Youtube" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
																</a>
															</td></tr>
														</tbody></table>
														<!--[if (mso)|(IE)]></td><![endif]-->


														<!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 0px;" valign="top"><![endif]-->
														<table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 0px">
															<tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
																<a href="https://www.instagram.com/jumuishalimited/" title="Instagram" target="_blank">
																	<img src="https://jumuisha.net/media/instagram.png" alt="Instagram" title="Instagram" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
																</a>
															</td></tr>
														</tbody></table>
														<!--[if (mso)|(IE)]></td><![endif]-->


														<!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
													</div>
												</div>

															</td>
														</tr>
													</tbody>
												</table>

												<table style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Calibri',sans-serif;" align="left">

													<table height="0px" align="center" border="0" cellpadding="0" cellspacing="0" width="82%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 1px solid #BBBBBB;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
														<tbody>
															<tr style="vertical-align: top">
																<td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;font-size: 0px;line-height: 0px;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
																	<span>&#160;</span>
																</td>
															</tr>
														</tbody>
													</table>

															</td>
														</tr>
													</tbody>
												</table>

												<table style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Calibri',sans-serif;" align="left">

													<div style="color: #908f8f; line-height: 190%; text-align: center; word-wrap: break-word;">
														<p style="font-size: 14px; line-height: 190%;">Want to change how you receive these emails?</p>
												<p style="font-size: 14px; line-height: 190%;">You can update your preferences or unsubscribe from this list.</p>
												<p style="font-size: 14px; line-height: 190%;">&nbsp;</p>
												<p style="font-size: 14px; line-height: 190%;">&copy; """+current_year_string+""" Jumuisha Limited. All Rights Reserved.</p>
													</div>

															</td>
														</tr>
													</tbody>
												</table>

													<!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
													</div>
												</div>
												<!--[if (mso)|(IE)]></td><![endif]-->
															<!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
														</div>
													</div>
												</div>



												<div class="u-row-container" style="padding: 0px;background-color: transparent">
													<div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
														<div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
															<!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: transparent;"><![endif]-->

												<!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
												<div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
													<div style="width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
													<!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

												<table style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:0px;font-family:'Calibri',sans-serif;" align="left">

												<table width="100%" cellpadding="0" cellspacing="0" border="0">
													<tr>
														<td style="padding-right: 0px;padding-left: 0px;" align="center">
														</td>
													</tr>
												</table>

															</td>
														</tr>
													</tbody>
												</table>

													<!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
													</div>
												</div>
												<!--[if (mso)|(IE)]></td><![endif]-->
															<!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
														</div>
													</div>
												</div>



												<div class="u-row-container" style="padding: 0px;background-color: transparent">
													<div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
														<div style="border-collapse: collapse;display: table;width: 100%;background-color: transparent;">
															<!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: transparent;"><![endif]-->

												<!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
												<div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
													<div style="width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
													<!--[if (!mso)&(!IE)]><!--><div style="padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

												<table style="font-family:'Calibri',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
													<tbody>
														<tr>
															<td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Calibri',sans-serif;" align="left">

													<table height="0px" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 0px solid #BBBBBB;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
														<tbody>
															<tr style="vertical-align: top">
																<td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;font-size: 0px;line-height: 0px;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
																	<span>&#160;</span>
																</td>
															</tr>
														</tbody>
													</table>

															</td>
														</tr>
													</tbody>
												</table>

													<!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
													</div>
												</div>
												<!--[if (mso)|(IE)]></td><![endif]-->
															<!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
														</div>
													</div>
												</div>


														<!--[if (mso)|(IE)]></td></tr></table><![endif]-->
														</td>
													</tr>
													</tbody>
													</table>
													<!--[if mso]></div><![endif]-->
													<!--[if IE]></div><![endif]-->
												</body>

												</html>

											"""
							data = {'email_body': email_body, 'to_email': user.email,
											'email_subject': 'Reset your passsword'}
							print('here is my data',data)

							# church = Church.objects.get(id=1)
							# # if str(user.id) != "26":
							# saveMessage = Message(
							#           user=user,
							#           church=church,
							#           message_type='email',
							#           subject='Reset your passsword',
							#           content='Reset your passsword',
							#           recepient=user.email
							#         )
							# saveMessage.save() 
							Util.send_email(data)  
					else:
							return Response('User with this email does not exist')
				elif phone_number:  
					print('first phone number', phone_number)
					
					if phone_number[0] == '0':
							phone_number = f'+254{phone_number[1:]}'
					elif phone_number[0] == '7':
							phone_number = f'+254{phone_number}'
					elif phone_number[0:3] == '254':
							phone_number  = f'+{phone_number}'
					else:
							phone_number = phone_number

					print('phone is here', phone_number)
					if User.objects.filter(phone_number=phone_number).exists():
							user = User.objects.get(phone_number=phone_number)
							uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
							token = PasswordResetTokenGenerator().make_token(user)
							current_site = get_current_site(request=request).domain

							relativeLink = reverse(
									'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

							redirect_url = "https://tig.citam.org/admin/#/change-password/"
							absurl = 'https://'+current_site + relativeLink
							reset_url = absurl+"?redirect_url="+redirect_url
							type_tiny = pyshorteners.Shortener()
							short_url = type_tiny.tinyurl.short(reset_url)
							print(short_url)

							message = f"Click this link {short_url} to reset your password "
										
							
					else:
							return Response('User with phone number does not exist')
				else:
						return Response({'error': 'Email and Phone Number was not found'}, status=status.HTTP_404_NOT_FOUND)
				return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
	
	permission_classes = [permissions.AllowAny]
	serializer_class = SetNewPasswordSerializer
	throttle_classes = [AnonRateThrottle]

	def get(self, request, uidb64, token):
		
		redirect_url = request.GET.get('redirect_url') + str('#/change-password/')

		# txt = redirect_url

		# redirect_url = txt.replace("/churches/", "/#/")

		try:
				id = smart_str(urlsafe_base64_decode(uidb64))
				user = User.objects.get(id=id)

				if not PasswordResetTokenGenerator().check_token(user, token):
						if len(redirect_url) > 3:
								return CustomRedirect(redirect_url+'?token_valid=False')
						else:
								return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

				if redirect_url and len(redirect_url) > 3:
						return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
				else:
						return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

		except DjangoUnicodeDecodeError as identifier:
				try:
						if not PasswordResetTokenGenerator().check_token(user):
								return CustomRedirect(redirect_url+'?token_valid=False')

				except UnboundLocalError as e:
						return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
	
	serializer_class = SetNewPasswordSerializer
	permission_classes = [AllowAny]
	throttle_classes = [AnonRateThrottle]

	def patch(self, request):
		
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)

class VerifyEmail(views.APIView):
	serializer_class = EmailVerificationSerializer
	renderer_classes = (UserRenderer,)
	throttle_classes = [AnonRateThrottle]

	token_param_config = openapi.Parameter(
			'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

	@swagger_auto_schema(manual_parameters=[token_param_config])
	def get(self, request):
			token = request.GET.get('token')
			callback_url = request.GET.get('callback_url')
			is_staff = request.GET.get('is_staff')
			callback_url = "https://tig.citam.org/admin/#/" + \
					callback_url+"?is_staff="+str(is_staff)
			# print(token)
			try:
					payload = jwt.decode(
							jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
					user = User.objects.get(id=payload['user_id'])
					if not user.is_verified:
							user.is_verified = True
							user.save()
					return CustomRedirect(callback_url+'?is_verified=True&message=Successfully activated')
					return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
			except jwt.ExpiredSignatureError as identifier:
					# return CustomRedirect('https://tig.citam.org/#/verification-invalid?is_verified=False&message=Activation Expired')
					return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
			except jwt.exceptions.DecodeError as identifier:
					# return CustomRedirect('https://tig.citam.org/#/verification-invalid?is_verified=False&message=Invalid Token')
					return Response({'error': 'Invalid token '+str(identifier)}, status=status.HTTP_400_BAD_REQUEST)
					


class EditUserAPIView(generics.RetrieveUpdateDestroyAPIView):
	queryset = User.objects.all()
	serializer_class = EditUserSerializer
	permission_classes = [permissions.IsAuthenticated, ]
	throttle_classes = [UserRateThrottle]
	lookup_field = 'id'
	

	def update(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.get_serializer(
				instance, data=request.data, partial=True)
		
		if serializer.is_valid():
			
			serializer.save()
			# return Response({"message": "user updated successfully"})
			return Response(serializer.data, status=status.HTTP_200_OK)

		else:
				return Response({"message": "failed", "details": serializer.errors})

	def delete(self, request, *args, **kwargs):
		instance = self.get_object()
		if instance:
			instance.delete()

			return Response(status=status.HTTP_204_NO_CONTENT)

		else:
			return Response(status=status.HTTP_404_NOT_FOUND)

class UsersListAPIView(generics.ListAPIView):
	serializer_class = UsersSerializer

	queryset = User.objects.filter(is_superuser=False).order_by('full_name')

	permission_classes = [permissions.IsAuthenticated]
	throttle_classes = [UserRateThrottle]
	filter_backends = [DjangoFilterBackend,
											filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ['full_name', 'id','id_number',
											'is_staff', 'phone_number', 'can_be_seen']
	search_fields = ['full_name', 'id', 'is_staff','id_number', 'phone_number']
	ordering_fields = ['full_name', 'id', 'is_staff','id_number', 'phone_number']



class LogoutAPIView(generics.GenericAPIView):
	
	serializer_class = LogoutSerializer

	throttle_classes = [UserRateThrottle]
	permission_classes = [permissions.IsAuthenticated, ]

	def post(self, request):
		
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(status=status.HTTP_204_NO_CONTENT)


		

