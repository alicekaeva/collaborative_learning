<?php

namespace App\Controller;

use App\Entity\Admin;
use App\Entity\Group;
use App\Entity\Message;
use App\Form\GroupType;
use App\Repository\AdminRepository;
use App\Repository\GroupRepository;
use App\Repository\MessageRepository;
use App\Repository\UserRepository;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
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

    #[Route('/new', name: 'app_group_new', methods: ['GET', 'POST'])]
    #[IsGranted('IS_AUTHENTICATED_FULLY')]
    public function new(Request $request, GroupRepository $groupRepository, AdminRepository $adminRepository, UserRepository $userRepository): Response
    {
        $group = new Group();
        $form = $this->createForm(GroupType::class, $group);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
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
            'group' => $group,
            'form' => $form,
        ]);
    }

    #[Route('/enroll', name: 'app_group_enroll', methods: ['POST'])]
    public function enroll(Request $request, MessageRepository $messageRepository, UserRepository $userRepository): Response
    {
        $user = $this->getUser();
        $receiverId = $request->request->get('receiver_id');
        $receiver = $userRepository->findOneBy(['id'=>$receiverId]);
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

    #[Route('/{id}/edit', name: 'app_group_edit', methods: ['GET', 'POST'])]
    #[IsGranted('IS_AUTHENTICATED_FULLY')]
    public function edit(Request $request, Group $group, GroupRepository $groupRepository): Response
    {
        $form = $this->createForm(GroupType::class, $group);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $groupRepository->save($group, true);

            return $this->redirectToRoute('app_group_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->renderForm('group/edit.html.twig', [
            'group' => $group,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_group_delete', methods: ['POST'])]
    #[IsGranted('IS_AUTHENTICATED_FULLY')]
    public function delete(Request $request, Group $group, GroupRepository $groupRepository): Response
    {
        if ($this->isCsrfTokenValid('delete' . $group->getId(), $request->request->get('_token'))) {
            $groupRepository->remove($group, true);
        }

        return $this->redirectToRoute('app_group_index', [], Response::HTTP_SEE_OTHER);
    }
}
