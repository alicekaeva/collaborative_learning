<?php

namespace App\Controller;

use App\Entity\Material;
use App\Entity\User;
use App\Form\MaterialType;
use App\Repository\CategoryRepository;
use App\Repository\GroupRepository;
use App\Repository\MaterialRepository;
use App\Repository\TagRepository;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\Form\FormError;
use Symfony\Component\HttpFoundation\File\Exception\FileException;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\String\Slugger\SluggerInterface;

#[Route('/material')]
#[IsGranted('IS_AUTHENTICATED_FULLY')]
class MaterialController extends AbstractController
{
    #[Route('/', name: 'app_material_index', methods: ['GET'])]
    public function index(MaterialRepository $materialRepository, Request $request, TagRepository $tagRepository, CategoryRepository $categoryRepository): Response
    {
        if ($request->query->has('tag')) {
            $tag = $tagRepository->findOneBy(['name' => $request->query->get('tag')]);
            $materials = $materialRepository->findMaterialsByTag($tag);
        } elseif ($request->query->has('category')) {
            $category = $categoryRepository->findOneBy(['name' => $request->query->get('category')]);
            $materials = $materialRepository->findMaterialsByCategory($category);
        } else {
            $materials = $materialRepository->findBy(['isPrivate' => 0]);
        }

        return $this->render('material/index.html.twig', [
            'materials' => $materials,
        ]);
    }

    #[Route('/recommended', name: 'app_material_recommended', methods: ['GET'])]
    #[IsGranted('IS_AUTHENTICATED_FULLY')]
    public function recommended(MaterialRepository $materialRepository): Response
    {
        /** @var User $user */
        $user = $this->getUser();
        $materials = $materialRepository->findRecommendedMaterials($user->getTags()->toArray());
        return $this->render('material/recommended.html.twig', [
            'materials' => $materials,
        ]);
    }

    #[Route('/new', name: 'app_material_new', methods: ['GET', 'POST'])]
    public function new(Request $request, MaterialRepository $materialRepository, GroupRepository $groupRepository, SluggerInterface $slugger): Response
    {
        $groupId = $request->cookies->get('currentGroup');
        $group = $groupRepository->findOneBy(['id' => $groupId]);
        if (!$group) {
            return new Response('Receiving group not found.', Response::HTTP_NOT_FOUND);
        }

        $material = new Material();
        $form = $this->createForm(MaterialType::class, $material);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $material->setCreatorGroup($group);
            $material->setCreatorUser($this->getUser());

            $file = $form->get('fileLink')->getData();
            $fileMimeType = $file->getMimeType();
            $mimeType = $form->get('mimeType')->getData();
            if ($mimeType != $fileMimeType) {
                $form->get('fileLink')->addError(new FormError('Тип загружаемого файла не совпадет с выбранным.'));
                return $this->renderForm('material/new.html.twig', [
                    'material' => $material,
                    'form' => $form,
                ]);
            }

            $originalFilename = pathinfo($file->getClientOriginalName(), PATHINFO_FILENAME);
            $safeFilename = $slugger->slug($originalFilename);
            $newFilename = $safeFilename . '-' . uniqid() . '.' . $file->guessExtension();
            $file->move($this->getParameter('material_directory'), $newFilename);
            $material->setFileLink($newFilename);

            $materialRepository->save($material, true);

            return $this->redirectToRoute('app_learning_show', ['id' => $groupId]);
        }

        return $this->renderForm('material/new.html.twig', [
            'material' => $material,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_material_show', methods: ['GET'])]
    public function show(Material $material): Response
    {
        return $this->render('material/show.html.twig', [
            'material' => $material,
        ]);
    }

    #[Route('/{id}/edit', name: 'app_material_edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, Material $material, MaterialRepository $materialRepository, SluggerInterface $slugger): Response
    {
        $form = $this->createForm(MaterialType::class, $material);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $file = $form->get('fileLink')->getData();
            $fileMimeType = $file->getMimeType();
            $mimeType = $form->get('mimeType')->getData();
            if ($mimeType != $fileMimeType) {
                $form->get('fileLink')->addError(new FormError('Тип загружаемого файла не совпадет с выбранным.'));
                return $this->renderForm('material/new.html.twig', [
                    'material' => $material,
                    'form' => $form,
                ]);
            }

            $originalFilename = pathinfo($file->getClientOriginalName(), PATHINFO_FILENAME);
            $safeFilename = $slugger->slug($originalFilename);
            $newFilename = $safeFilename . '-' . uniqid() . '.' . $file->guessExtension();
            $file->move($this->getParameter('material_directory'), $newFilename);
            $material->setFileLink($newFilename);

            $materialRepository->save($material, true);

            return $this->redirectToRoute('app_learning_show', ['id' => $material->getCreatorGroup()->getId()]);
        }

        return $this->renderForm('material/edit.html.twig', [
            'material' => $material,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_material_delete', methods: ['POST'])]
    public function delete(Request $request, Material $material, MaterialRepository $materialRepository): Response
    {
        if ($this->isCsrfTokenValid('delete' . $material->getId(), $request->request->get('_token'))) {
            $filePath = $this->getParameter('material_directory') . '/' . $material->getFileLink();
            if (file_exists($filePath)) {
                unlink($filePath);
            }

            $materialRepository->remove($material, true);
        }

        return $this->redirect($request->headers->get('referer'));
    }
}
