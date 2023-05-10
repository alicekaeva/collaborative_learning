<?php

namespace App\Controller;

use App\Entity\Group;
use App\Entity\Message;
use App\Entity\Student;
use App\Entity\Teacher;
use App\Entity\User;
use App\Repository\GroupRepository;
use App\Repository\MessageRepository;
use App\Repository\StudentRepository;
use App\Repository\TeacherRepository;
use App\Repository\UserRepository;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

#[Route('/learning')]
#[IsGranted('IS_AUTHENTICATED_FULLY')]
class LearningController extends AbstractController
{
    #[Route('/', name: 'app_learning_index', methods: ['GET'])]
    public function index(GroupRepository $groupRepository): Response
    {
        $user = $this->getUser();
        $groups = $groupRepository->findAllGroupsForUser($user);

        return $this->render('learning/index.html.twig', [
            'groups' => $groups,
            'activeGroup' => null,
        ]);
    }

    #[Route('/group/{id}', name: 'app_learning_show', methods: ['GET'])]
    public function show(MessageRepository $messageRepository, GroupRepository $groupRepository, Group $receivingGroup, UserRepository $userRepository): Response
    {
        $user = $this->getUser();
        $groups = $groupRepository->findAllGroupsForUser($user);
        $chat = $messageRepository->findGroupChat($receivingGroup);

        return $this->render('learning/index.html.twig', [
            'groups' => $groups,
            'activeGroup' => $receivingGroup,
            'chat' => $chat,
            'users' => $userRepository->findAll()
        ]);
    }

    #[Route('/send', name: 'app_learning_send', methods: ['POST'])]
    public function send(Request $request, MessageRepository $messageRepository, GroupRepository $groupRepository): Response
    {
        $user = $this->getUser();
        $receiverId = $request->request->get('receiver_id');
        $receiver = $groupRepository->findOneBy(['id' => $receiverId]);
        $content = $request->request->get('content');

        $message = new Message();
        $message->setSender($user);
        $message->setReceivingGroup($receiver);
        $message->setContent($content);
        $message->setSendingDate(new \DateTimeImmutable());
        $messageRepository->save($message, true);

        return $this->redirectToRoute('app_learning_show', ['id' => $receiverId]);
    }

    #[Route('/add_user', name: 'app_learning_add_user', methods: ['POST'])]
    public function addUserToGroup(Request $request, TeacherRepository $teacherRepository, StudentRepository $studentRepository, UserRepository $userRepository, GroupRepository $groupRepository): Response
    {
        $groupId = $request->request->get('group_id');
        $group = $groupRepository->findOneBy(['id' => $groupId]);
        $userId = $request->request->get('user');
        $user = $userRepository->findOneBy(['id' => $userId]);
        $role = $request->request->get('role');
        if ($role == 'teacher'){
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
        } elseif ($role == 'student'){
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
        return $this->redirectToRoute('app_learning_show', ['id' => $groupId]);
    }
}