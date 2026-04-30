import { createBrowserRouter } from 'react-router-dom'

import AppLayout from '../components/layout/AppLayout'
import AdminIngredientsPage from '../pages/admin/AdminIngredientsPage'
import AdminRecipesPage from '../pages/admin/AdminRecipesPage'
import HomePage from '../pages/HomePage'
import RecipeDetailsPage from '../pages/RecipeDetailsPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'recipe/:id', element: <RecipeDetailsPage /> },
      { path: 'admin/recipes', element: <AdminRecipesPage /> },
      { path: 'admin/ingredients', element: <AdminIngredientsPage /> },
    ],
  },
])
