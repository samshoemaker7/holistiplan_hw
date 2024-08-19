from django.test import TestCase, Client
from django.urls import reverse
from snippets.models import ExtendedUser, Audit

# Create your tests here.
class UserTest(TestCase):
    def tearDown(self):
        ExtendedUser.objects.all().delete()

    def testCreateUser(self):
        user = ExtendedUser.objects.create_user(username="test", password="12345")
        
        self.assertEqual(user.username, "test")
    
    def testSoftDeleteUser(self):
        user = ExtendedUser.objects.create_user(username="test", password="12345")

        self.assertEqual(user.username, "test")
        self.assertEquals(user.is_deleted, False)

        user.soft_delete()

        user.save()

        self.assertEquals(user.is_deleted, True)

class UserListViewTest(TestCase):
    def tearDown(self):
        ExtendedUser.objects.all().delete()

    def testListViewEmpty(self):
        list_url = reverse('user-list')
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['count'], 0)

    def testListViewEntries(self):
        user_one = ExtendedUser.objects.create_user(username="user1", password="1234")
        user_two = ExtendedUser.objects.create_user(username="user2", password="1234")
        user_ids = [user_one.pk, user_two.pk]

        list_url = reverse('user-list')
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['count'], 2)

        results_ids = []
        for entry in res.data['results']:
            id = entry['id']
            results_ids.append(id)
        
        self.assertEqual(results_ids, user_ids)

    def testListViewSoftDelete(self):
        user_one = ExtendedUser.objects.create_user(username="user1", password="1234")
        user_two = ExtendedUser.objects.create_user(username="user2", password="1234")

        user_one.soft_delete()
        user_one.save()

        list_url = reverse('user-list')
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['count'], 1)

        self.assertEqual(res.data['results'][0]['id'], user_two.pk)

class UserDetailViewTest(TestCase):
    def tearDown(self):
        ExtendedUser.objects.all().delete()

    def testDetailViewInvalid(self):
        list_url = reverse('extendeduser-detail', args=['1234'])
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 404)

    def testDetailViewValid(self):
        user_one = ExtendedUser.objects.create_user(username="user1", password="1234")

        list_url = reverse('extendeduser-detail', args=[user_one.pk])
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 200)

    def testDetailViewHidden(self):
        user_one = ExtendedUser.objects.create_user(username="user1", password="1234")

        user_one.soft_delete()
        user_one.save()

        list_url = reverse('extendeduser-detail', args=[user_one.pk])
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 404)

class AuditTest(TestCase):
    def tearDown(self):
        ExtendedUser.objects.all().delete()
        Audit.objects.all().delete()

    def testCreateAudit(self):
        audit_log = Audit.objects.create(model_name="ExtendedUser", action="create")

        self.assertEqual(audit_log.model_name, "ExtendedUser")
        self.assertEqual(audit_log.action, "create")

    def testGenerateCreateAudit(self):
        new_user = ExtendedUser.objects.create_user(username="test", password="1234")

        audit_entry = Audit.objects.filter(object_id=new_user.pk, action="create")
        self.assertEqual(len(audit_entry), 1)

    def testGenerateUpdateAudit(self):
        new_user = ExtendedUser.objects.create_user(username="test", password="1234")

        new_user.email = "email@email.com"
        new_user.save()

        audit_entry = Audit.objects.filter(object_id=new_user.pk, action="update")
        self.assertEqual(len(audit_entry), 1)

    def testGenerateSoftDeleteAudit(self):
        new_user = ExtendedUser.objects.create_user(username="test", password="1234")

        new_user.soft_delete()
        new_user.save()

        audit_entry = Audit.objects.filter(object_id=new_user.pk, action="update")
        self.assertEqual(len(audit_entry), 1)

    def testGenerateDeleteAudit(self):
        new_user = ExtendedUser.objects.create_user(username="test", password="1234")
        id = new_user.pk

        new_user.delete()
        new_user.save()

        audit_entry = Audit.objects.filter(object_id=id, action="destroy")
        self.assertEqual(len(audit_entry), 1)

class AuditListViewTest(TestCase):
    def setUp(self):
        staff_user = ExtendedUser.objects.create_user(username="staff1", password="password", is_staff=True)
        self.client = Client()
        self.client.force_login(staff_user)

    def tearDown(self):
        Audit.objects.all().delete()

    def testListViewEmpty(self):
        list_url = reverse('audit-list')
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 200)

    def testListViewEntries(self):
        audit_one = Audit.objects.create(model_name="ExtendedUser", action="create")
        audit_two = Audit.objects.create(model_name="ExtendedUser", action="create")

        list_url = reverse('audit-list')
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['count'], 4)

    def testListViewNotAuth(self):
        self.client.logout()
        list_url = reverse('audit-list')
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 401)

class AuditDetailViewTest(TestCase):
    def setUp(self):
        staff_user = ExtendedUser.objects.create_user(username="staff1", password="password", is_staff=True)
        self.client = Client()
        self.client.force_login(staff_user)

    def tearDown(self):
        Audit.objects.all().delete()

    def testDetailViewInvalid(self):
        list_url = reverse('audit-detail', args=['1234'])
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 404)

    def testDetailViewValid(self):
        audit_one = Audit.objects.create(model_name="ExtendedUser", action="create")

        list_url = reverse('audit-detail', args=[audit_one.pk])
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 200)

    def testDetailViewNotAuth(self):
        audit_one = Audit.objects.create(model_name="ExtendedUser", action="create")

        self.client.logout()

        list_url = reverse('audit-detail', args=[audit_one.pk])
        res = self.client.get(list_url)
        
        self.assertEqual(res.status_code, 401)