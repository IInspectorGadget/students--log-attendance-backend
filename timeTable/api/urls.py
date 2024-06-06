from django.urls import include, path
from .views import AttendanceDateListView, AttendanceDetailView, AttendanceReportGroupCompleteApiView, AttendanceReportGroupDetailView, AttendanceReportViewSet, AttendanceReportsCreateEditAPIView, AttendanceListView, AttendanceReportCreateEditAPIView, AttendanceViewSet, CourseViewSet, CustomUserViewSet, FacultyViewSet, GroupDetail, GroupListApiView, GroupViewSet, JournalApiView, MyTokenObtainPairView, StudentAttendanceReportList, StudentViewSet, StudentsList, SubjectJournalApiView, SubjectRealizationListView, SubjectRealizationViewSet, SubjectViewSet, TeacherAttendanceReportList, TeacherViewSet, TeachersList
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'faculties', FacultyViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'students', StudentViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'subject-realizations', SubjectRealizationViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'attendance-reports', AttendanceReportViewSet)


urlpatterns = [
    path('crud/', include(router.urls)),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # path('attendanceDate/', AttendanceDateListView.as_view(), name='teacher_attendanceDate_list'),

    path('attendance/', AttendanceListView.as_view(), name='teacher_attendance_list'),
    path('attendanceDetail/<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('attendanceComplete/<int:pk>', AttendanceReportGroupCompleteApiView.as_view(), name='attendanceGroupComplete'),
    path('attendanceDetail/<int:pk>/<int:group_pk>', AttendanceReportGroupDetailView.as_view(), name='attendanceGroup'),

    path('attendanceReport/', AttendanceReportCreateEditAPIView.as_view(), name='attendance_report'),
    path('attendanceReports/', AttendanceReportsCreateEditAPIView.as_view(), name='attendance_reports'),

    path('subjects/', SubjectRealizationListView.as_view(), name="subjects"),
    path('groups/<int:pk>/', GroupListApiView.as_view(), name="groups"),
    path('groups/<int:subject_id>/<int:group_id>', SubjectJournalApiView.as_view(), name="attendanceGroup"),

    path('groups/', GroupListApiView.as_view(), name="groups"),
    path('journal/<int:group_id>/', JournalApiView.as_view(), name="attendanceGroup"),

    path('student/<int:user_id>', StudentAttendanceReportList.as_view(), name="StudentData"),
    path('teacher/<int:user_id>', TeacherAttendanceReportList.as_view(), name="TeacherData"),
    path('group/<int:group_id>', GroupDetail.as_view(), name="GroupData"),
    # path('teacher/<int:teacher_id>', GroupDetail.as_view(), name="StudentData"),

    path('students/', StudentsList.as_view(), name="StudentsList"),
    path('teachers/', TeachersList.as_view(), name="TeachersList"),
    path('groups/', GroupListApiView.as_view(), name="GroupsList"),



]
