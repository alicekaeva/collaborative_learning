<?php

namespace App\Controller;

use App\Entity\Tag;
use App\Form\TagType;
use App\Repository\CategoryRepository;
use App\Repository\TagRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\HttpFoundation\JsonResponse;

#[Route('/tag')]
class TagController extends AbstractController
{
    #[Route('/', name: 'app_tag_index', methods: ['GET'])]
    public function index(TagRepository $tagRepository): Response
    {
        return $this->render('tag/index.html.twig', [
            'tags' => $tagRepository->findAll(),
        ]);
    }

    #[Route('/get_tags/{categoryId}', name: 'app_get_tags', methods: ['GET'])]
    public function getTags(int $categoryId, TagRepository $tagRepository): JsonResponse
    {
        $tags = $tagRepository->findBy(['category' => $categoryId]);

        $tagData = [];
        foreach ($tags as $tag) {
            $tagData[] = [
                'id' => $tag->getId(),
                'name' => $tag->getName(),
            ];
        }

        return new JsonResponse($tagData);
    }

    #[Route('/new', name: 'app_tag_new', methods: ['GET', 'POST'])]
    public function new(Request $request, TagRepository $tagRepository, CategoryRepository $categoryRepository): Response
    {
        if ($request->isMethod('POST')) {
            $name = $request->request->get('new_tag');
            $category_id = $request->request->get('category');
            $category = $categoryRepository->findOneBy(['id' => $category_id]);
            $tag = $tagRepository->findBy(['name' => $name]);
            if (!$tag) {
                $tag = new Tag();
                $tag->setName($name);
                $tag->setCategory($category);
                $tagRepository->save($tag, true);
            }
        }
        return $this->redirect($request->headers->get('referer'));
    }

    #[Route('/{id}', name: 'app_tag_show', methods: ['GET'])]
    public function show(Tag $tag): Response
    {
        return $this->render('tag/show.html.twig', [
            'tag' => $tag,
        ]);
    }

    #[Route('/{id}/edit', name: 'app_tag_edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, Tag $tag, TagRepository $tagRepository): Response
    {
        $form = $this->createForm(TagType::class, $tag);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $tagRepository->save($tag, true);

            return $this->redirectToRoute('app_tag_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->renderForm('tag/edit.html.twig', [
            'tag' => $tag,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_tag_delete', methods: ['POST'])]
    public function delete(Request $request, Tag $tag, TagRepository $tagRepository): Response
    {
        if ($this->isCsrfTokenValid('delete'.$tag->getId(), $request->request->get('_token'))) {
            $tagRepository->remove($tag, true);
        }

        return $this->redirectToRoute('app_tag_index', [], Response::HTTP_SEE_OTHER);
    }
}
