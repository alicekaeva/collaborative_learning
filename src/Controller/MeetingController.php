<?php

namespace App\Controller;

use App\Entity\Meeting;
use App\Form\MeetingType;
use App\Repository\GroupRepository;
use App\Repository\MeetingRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

#[Route('/meeting')]
class MeetingController extends AbstractController
{
    #[Route('/', name: 'app_meeting_index', methods: ['GET'])]
    public function index(MeetingRepository $meetingRepository): Response
    {
        return $this->render('meeting/index.html.twig', [
            'meetings' => $meetingRepository->findAll(),
        ]);
    }

    #[Route('/new', name: 'app_meeting_new', methods: ['GET', 'POST'])]
    public function new(Request $request, MeetingRepository $meetingRepository, GroupRepository $groupRepository): Response
    {
        $groupId = $request->cookies->get('currentGroup');
        $group = $groupRepository->findOneBy(['id' => $groupId]);
        if (!$group) {
            return new Response('Receiving group not found.', Response::HTTP_NOT_FOUND);
        }

        $meeting = new Meeting();
        $form = $this->createForm(MeetingType::class, $meeting);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $meeting->setCreator($group);
            $meetingRepository->save($meeting, true);

            return $this->redirectToRoute('app_learning_show', ['id' => $groupId]);
        }

        return $this->renderForm('meeting/new.html.twig', [
            'meeting' => $meeting,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_meeting_show', methods: ['GET'])]
    public function show(Meeting $meeting): Response
    {
        return $this->render('meeting/show.html.twig', [
            'meeting' => $meeting,
        ]);
    }

    #[Route('/{id}/edit', name: 'app_meeting_edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, Meeting $meeting, MeetingRepository $meetingRepository): Response
    {
        $form = $this->createForm(MeetingType::class, $meeting);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $meetingRepository->save($meeting, true);

            return $this->redirectToRoute('app_learning_show', ['id' => $meeting->getCreator()->getId()]);
        }

        return $this->renderForm('meeting/edit.html.twig', [
            'meeting' => $meeting,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_meeting_delete', methods: ['POST'])]
    public function delete(Request $request, Meeting $meeting, MeetingRepository $meetingRepository): Response
    {
        if ($this->isCsrfTokenValid('delete'.$meeting->getId(), $request->request->get('_token'))) {
            $meetingRepository->remove($meeting, true);
        }

        return $this->redirect($request->headers->get('referer'));
    }
}
