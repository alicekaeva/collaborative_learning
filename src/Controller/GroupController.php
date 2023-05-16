<?php

namespace App\Controller;

use App\Entity\Admin;
use App\Entity\Group;
use App\Entity\Message;
use App\Entity\Student;
use App\Entity\Teacher;
use App\Repository\AdminRepository;
use App\Repository\CategoryRepository;
use App\Repository\GroupRepository;
use App\Repository\MessageRepository;
use App\Repository\StudentRepository;
use App\Repository\TagRepository;
use App\Repository\TeacherRepository;
use App\Repository\UserRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

#[Route('/group')]
class GroupController extends AbstractController
{
    #[Route('/', name: 'app_group_index', methods: ['GET'])]
    public function index(GroupRepository $groupRepository): Response
    {
        return $this->render('group/index.html.twig', [
            'groups' => $groupRepository->findAll(),
        ]);
    }

    #[Route('/{groupId}/users/{userId}', name: 'group_user_role', methods: ['GET'])]
    public function getUserRoleInGroup(int $groupId, int $userId, GroupRepository $groupRepository, TeacherRepository $teacherRepository, StudentRepository $studentRepository, UserRepository $userRepository): JsonResponse
    {
        $group = $groupRepository->findOneBy(['id' => $groupId]);
        if (!$group) {
            return new JsonResponse(['error' => 'Group not found.'], Response::HTTP_NOT_FOUND);
        }

        $students = $group->getStudents();
        $teachers = $group->getTeachers();

        $user = $userRepository->findOneBy(['id' => $userId]);
        if (!$user) {
            return new JsonResponse(['error' => 'User not found.'], Response::HTTP_NOT_FOUND);
        }

        $student = $studentRepository->findOneBy(['user' => $user]);
        $teacher = $teacherRepository->findOneBy(['user' => $user]);

        $isStudentInGroup = $students->contains($student);
        $isTeacherInGroup = $teachers->contains($teacher);

        if ($isStudentInGroup) {
            return new JsonResponse(['role' => 'ROLE_STUDENT']);
        } elseif ($isTeacherInGroup) {
            return new JsonResponse(['role' => 'ROLE_TEACHER']);
        } else {
            return new JsonResponse(['role' => 'ROLE_NONE']);
        }
    }

    #[Route('/new', name: 'app_group_new', methods: ['GET', 'POST'])]
    public function new(Request $request, GroupRepository $groupRepository, AdminRepository $adminRepository, UserRepository $userRepository, TagRepository $tagRepository, CategoryRepository $categoryRepository): Response
    {
        if ($request->isMethod('POST')) {
            $name = $request->request->get('group_name');
            $info = $request->request->get('info');
            $teachers = $request->request->get('teachers');
            $students = $request->request->get('students');
            $parameters = $request->request->all();
            $tagIds = $parameters['tags'];
            $group = new Group();
            $group->setName($name);
            $group->setInfo($info);
            $group->setRequiredTeachers($teachers);
            $group->setRequiredStudents($students);
            $tags = $tagRepository->findBy(['id' => $tagIds]);
            foreach ($tags as $tag) {
                $group->addTag($tag);
            }
            $user = $this->getUser();
            $admin = $adminRepository->findOneBy(['user' => $user]);
            if (!$admin) {
                $admin = new Admin();
                $admin->setUser($user);
                $adminRepository->save($admin, true);
                $userRoles = $user->getRoles();
                $userRoles[] = 'ROLE_ADMIN';
                $user->setRoles($userRoles);
                $userRepository->save($user, true);
            }
            $group->setAdministrator($admin);
            $groupRepository->save($group, true);
            return $this->redirectToRoute('app_group_index', [], Response::HTTP_SEE_OTHER);
        }
        return $this->renderForm('group/new.html.twig', [
            'categories' => $categoryRepository->findAll(),
        ]);
    }

    #[Route('/enroll', name: 'app_group_enroll', methods: ['POST'])]
    public function enroll(Request $request, MessageRepository $messageRepository, UserRepository $userRepository): Response
    {
        $user = $this->getUser();
        $receiverId = $request->request->get('receiver_id');
        $receiver = $userRepository->findOneBy(['id' => $receiverId]);
        $groupName = $request->request->get('group_name');
        $content = 'Привет! Я хочу присоединиться к вашей группе ' . $groupName . '. Можешь добавить меня?';

        $message = new Message();
        $message->setSender($user);
        $message->setReceiver($receiver);
        $message->setContent($content);
        $message->setSendingDate(new \DateTimeImmutable());
        $messageRepository->save($message, true);

        return $this->redirectToRoute('app_message_show', ['id' => $receiverId]);
    }

    #[Route('/{id}', name: 'app_group_show', methods: ['GET'])]
    public function show(Group $group): Response
    {
        return $this->render('group/show.html.twig', [
            'group' => $group,
        ]);
    }

    #[Route('/{id}/management', name: 'app_group_management', methods: ['GET', 'POST'])]
    public function management (Group $group, UserRepository $userRepository): Response
    {
        return $this->renderForm('group/management.html.twig', [
            'group' => $group,
            'users' => $userRepository->findAll()
        ]);
    }

    #[Route('/{id}/edit', name: 'app_group_edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, Group $group, GroupRepository $groupRepository, TagRepository $tagRepository): Response
    {
        if ($request->isMethod('POST')) {
            $name = $request->request->get('group_name');
            $info = $request->request->get('info');
            $teachers = $request->request->get('teachers');
            $students = $request->request->get('students');
            $parameters = $request->request->all();
            $tagIds = $parameters['tags'];
            $group->setName($name);
            $group->setInfo($info);
            $group->setRequiredTeachers($teachers);
            $group->setRequiredStudents($students);
            $tags = $tagRepository->findBy(['id' => $tagIds]);
            $groupTags = $group->getTags();
            foreach ($groupTags as $groupTag) {
                if (!in_array($groupTag->getId(), $tagIds)) {
                    $group->removeTag($groupTag);
                }
            }
            foreach ($tags as $tag) {
                $group->addTag($tag);
            }
            $groupRepository->save($group, true);
            return $this->redirectToRoute('app_learning_show', ['id' => $group->getId()], Response::HTTP_SEE_OTHER);
        }
        return $this->renderForm('group/edit.html.twig', [
            'group' => $group
        ]);
    }

    #[Route('/add_user', name: 'app_group_add_user', methods: ['POST'])]
    public function addUserToGroup(Request $request, TeacherRepository $teacherRepository, StudentRepository $studentRepository, UserRepository $userRepository, GroupRepository $groupRepository): Response
    {
        $groupId = $request->request->get('group_id');
        $group = $groupRepository->findOneBy(['id' => $groupId]);
        $userId = $request->request->get('user');
        $user = $userRepository->findOneBy(['id' => $userId]);
        $role = $request->request->get('role');
        if ($role == 'teacher') {
            $teacher = $teacherRepository->findOneBy(['user' => $user]);
            if (!$teacher) {
                $teacher = new Teacher();
                $teacher->setUser($user);
                $teacherRepository->save($teacher, true);
                $userRoles = $user->getRoles();
                $userRoles[] = 'ROLE_TEACHER';
                $user->setRoles($userRoles);
                $userRepository->save($user, true);
            }
            $group->addTeacher($teacher);
            $groupRepository->save($group, true);
        } elseif ($role == 'student') {
            $student = $studentRepository->findOneBy(['user' => $user]);
            if (!$student) {
                $student = new Student();
                $student->setUser($user);
                $studentRepository->save($student, true);
                $userRoles = $user->getRoles();
                $userRoles[] = 'ROLE_STUDENT';
                $user->setRoles($userRoles);
                $userRepository->save($user, true);
            }
            $group->addStudent($student);
            $groupRepository->save($group, true);
        }
        return $this->redirectToRoute('app_group_management', ['id' => $groupId]);
    }

    #[Route('/edit_user', name: 'app_group_edit_user', methods: ['POST'])]
    public function editUser(Request $request, TeacherRepository $teacherRepository, StudentRepository $studentRepository, UserRepository $userRepository, GroupRepository $groupRepository): Response
    {
        $groupId = $request->request->get('group_id');
        $group = $groupRepository->findOneBy(['id' => $groupId]);
        $participantId = $request->request->get('participant');
        $participant = $userRepository->findOneBy(['id' => $participantId]);
        $role = $request->request->get('role');
        if ($role == 'teacher') {
            $students = $group->getStudents();
            $student = $studentRepository->findOneBy(['user' => $participant]);
            if (in_array($student, $students->toArray())) {
                $group->removeStudent($student);
                $teacher = $teacherRepository->findOneBy(['user' => $participant]);
                if (!$teacher) {
                    $teacher = new Teacher();
                    $teacher->setUser($participant);
                    $teacherRepository->save($teacher, true);
                    $userRoles = $participant->getRoles();
                    $userRoles[] = 'ROLE_TEACHER';
                    $participant->setRoles($userRoles);
                    $userRepository->save($participant, true);
                }
                $group->addTeacher($teacher);
                $groupRepository->save($group, true);
            }
        } elseif ($role == 'student') {
            $teachers = $group->getTeachers();
            $teacher = $teacherRepository->findOneBy(['user' => $participant]);
            if (in_array($teacher, $teachers->toArray())) {
                $group->removeTeacher($teacher);
                $student = $studentRepository->findOneBy(['user' => $participant]);
                if (!$student) {
                    $student = new Student();
                    $student->setUser($participant);
                    $studentRepository->save($student, true);
                    $userRoles = $participant->getRoles();
                    $userRoles[] = 'ROLE_STUDENT';
                    $participant->setRoles($userRoles);
                    $userRepository->save($participant, true);
                }
                $group->addStudent($student);
                $groupRepository->save($group, true);
            }
        }
        return $this->redirectToRoute('app_group_management', ['id' => $groupId]);
    }

    #[Route('/delete_user', name: 'app_group_delete_user', methods: ['POST'])]
    public function deleteUser(Request $request, GroupRepository $groupRepository, StudentRepository $studentRepository, TeacherRepository $teacherRepository, UserRepository $userRepository): Response
    {
        $groupId = $request->request->get('group_id');
        $group = $groupRepository->findOneBy(['id' => $groupId]);
        $students = $group->getStudents();
        $teachers = $group->getTeachers();

        $userId = $request->request->get('user_to_delete');
        $user = $userRepository->findOneBy(['id' => $userId]);

        $student = $studentRepository->findOneBy(['user' => $user]);
        $teacher = $teacherRepository->findOneBy(['user' => $user]);

        if ($student && $students->contains($student)) {
            $group->removeStudent($student);
        } elseif ($teacher && $teachers->contains($teacher)) {
            $group->removeTeacher($teacher);
        }

        $groupRepository->save($group, true);
        return $this->redirectToRoute('app_group_management', ['id' => $groupId]);
    }

    #[Route('/{id}', name: 'app_group_delete', methods: ['POST'])]
    public function delete(Request $request, Group $group, GroupRepository $groupRepository): Response
    {
        if ($this->isCsrfTokenValid('delete' . $group->getId(), $request->request->get('_token'))) {
            $groupRepository->remove($group, true);
        }

        return $this->redirectToRoute('app_learning_index', [], Response::HTTP_SEE_OTHER);
    }
}
