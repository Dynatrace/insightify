import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/insightify/blog',
    component: ComponentCreator('/insightify/blog', 'b7b'),
    exact: true
  },
  {
    path: '/insightify/blog/archive',
    component: ComponentCreator('/insightify/blog/archive', '09f'),
    exact: true
  },
  {
    path: '/insightify/blog/first-blog-post',
    component: ComponentCreator('/insightify/blog/first-blog-post', '010'),
    exact: true
  },
  {
    path: '/insightify/blog/long-blog-post',
    component: ComponentCreator('/insightify/blog/long-blog-post', '2d9'),
    exact: true
  },
  {
    path: '/insightify/blog/mdx-blog-post',
    component: ComponentCreator('/insightify/blog/mdx-blog-post', 'd9d'),
    exact: true
  },
  {
    path: '/insightify/blog/tags',
    component: ComponentCreator('/insightify/blog/tags', '0a3'),
    exact: true
  },
  {
    path: '/insightify/blog/tags/docusaurus',
    component: ComponentCreator('/insightify/blog/tags/docusaurus', 'f83'),
    exact: true
  },
  {
    path: '/insightify/blog/tags/facebook',
    component: ComponentCreator('/insightify/blog/tags/facebook', '6d0'),
    exact: true
  },
  {
    path: '/insightify/blog/tags/hello',
    component: ComponentCreator('/insightify/blog/tags/hello', 'dab'),
    exact: true
  },
  {
    path: '/insightify/blog/tags/hola',
    component: ComponentCreator('/insightify/blog/tags/hola', '3b9'),
    exact: true
  },
  {
    path: '/insightify/blog/welcome',
    component: ComponentCreator('/insightify/blog/welcome', '420'),
    exact: true
  },
  {
    path: '/insightify/markdown-page',
    component: ComponentCreator('/insightify/markdown-page', 'e26'),
    exact: true
  },
  {
    path: '/insightify/docs',
    component: ComponentCreator('/insightify/docs', '15b'),
    routes: [
      {
        path: '/insightify/docs/Advanced use-cases',
        component: ComponentCreator('/insightify/docs/Advanced use-cases', '720'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/insightify/docs/get-started',
        component: ComponentCreator('/insightify/docs/get-started', '44f'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/insightify/docs/Guides',
        component: ComponentCreator('/insightify/docs/Guides', '32c'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/insightify/docs/intro',
        component: ComponentCreator('/insightify/docs/intro', 'fc5'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/insightify/docs/Quick-Links',
        component: ComponentCreator('/insightify/docs/Quick-Links', '51d'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/insightify/docs/Troubleshooting',
        component: ComponentCreator('/insightify/docs/Troubleshooting', '386'),
        exact: true,
        sidebar: "tutorialSidebar"
      }
    ]
  },
  {
    path: '/insightify/',
    component: ComponentCreator('/insightify/', '95c'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
