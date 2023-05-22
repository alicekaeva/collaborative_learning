<?php

namespace App\Controller;

use App\Entity\Goal;
use App\Form\GoalType;
use App\Repository\GoalRepository;
use App\Repository\GroupRepository;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

#[Route('/goal')]
#[IsGranted('IS_AUTHENTICATED_FULLY')]
class GoalController extends AbstractController
{
    #[Route('/', name: 'app_goal_index', methods: ['GET'])]
    public function index(GoalRepository $goalRepository): Response
    {
        return $this->render('goal/index.html.twig', [
            'goals' => $goalRepository->findAll(),
        ]);
    }

    #[Route('/new', name: 'app_goal_new', methods: ['GET', 'POST'])]
    public function new(Request $request, GoalRepository $goalRepository, GroupRepository $groupRepository): Response
    {
        $groupId = $request->cookies->get('currentGroup');
        $group = $groupRepository->findOneBy(['id' => $groupId]);
        if (!$group) {
            return new Response('Receiving group not found.', Response::HTTP_NOT_FOUND);
        }

        $goal = new Goal();
        $form = $this->createForm(GoalType::class, $goal);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $goal->setCreator($group);
            $goal->setCompleted(false);
            $goalRepository->save($goal, true);

            return $this->redirectToRoute('app_learning_show', ['id' => $groupId]);
        }

        return $this->renderForm('goal/new.html.twig', [
            'goal' => $goal,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_goal_show', methods: ['GET'])]
    public function show(Goal $goal): Response
    {
        return $this->render('goal/show.html.twig', [
            'goal' => $goal,
        ]);
    }

    #[Route('/{id}/edit', name: 'app_goal_edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, Goal $goal, GoalRepository $goalRepository): Response
    {
        $form = $this->createForm(GoalType::class, $goal);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $goalRepository->save($goal, true);

            return $this->redirectToRoute('app_learning_show', ['id' => $goal->getCreator()->getId()]);
        }

        return $this->renderForm('goal/edit.html.twig', [
            'goal' => $goal,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_goal_delete', methods: ['POST'])]
    public function delete(Request $request, Goal $goal, GoalRepository $goalRepository): Response
    {
        if ($this->isCsrfTokenValid('delete' . $goal->getId(), $request->request->get('_token'))) {
            $goalRepository->remove($goal, true);
        }

        return $this->redirect($request->headers->get('referer'));
    }

    #[Route('/complete/{id}', name: 'app_complete')]
    public function complete(Goal $goal, GoalRepository $goals, Request $request): Response
    {
        $goal->setCompleted(true);
        $goals->save($goal, true);

        return $this->redirect($request->headers->get('referer'));
    }

    #[Route('/uncomplete/{id}', name: 'app_uncomplete')]
    public function uncomplete(Goal $goal, GoalRepository $goals, Request $request): Response
    {
        $goal->setCompleted(false);
        $goals->save($goal, true);

        return $this->redirect($request->headers->get('referer'));
    }
}
