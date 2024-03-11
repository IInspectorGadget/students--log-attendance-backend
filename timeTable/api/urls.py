from django.urls import path
from .views import AttendanceDetailView, AttendanceReportGroupCompleteApiView, AttendanceReportGroupDetailView, AttendanceReportsCreateEditAPIView, AttendanceListView, AttendanceReportCreateEditAPIView, GroupListApiView, JournalApiView, MyTokenObtainPairView, SubjectRealizationListView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('attendance/', AttendanceListView.as_view(), name='teacher_attendance_list'),
    path('attendanceDetail/<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('attendanceComplete/<int:pk>', AttendanceReportGroupCompleteApiView.as_view(), name='attendanceGroupComplete'),
    path('attendanceDetail/<int:pk>/<int:group_pk>', AttendanceReportGroupDetailView.as_view(), name='attendanceGroup'),

    path('attendanceReport/', AttendanceReportCreateEditAPIView.as_view(), name='attendance_report'),
    path('attendanceReports/', AttendanceReportsCreateEditAPIView.as_view(), name='attendance_reports'),

    path('subjects/', SubjectRealizationListView.as_view(), name="subjects"),
    path('groups/<int:pk>/', GroupListApiView.as_view(), name="groups"),
    path('groups/<int:subject_realization_id>/<int:group_id>', JournalApiView.as_view(), name="attendanceGroup"),


]
