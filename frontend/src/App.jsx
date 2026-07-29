import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./features/auth/AuthContext.jsx";
import RegisterPage from "./features/auth/RegisterPage.jsx";
import LoginPage from "./features/auth/LoginPage.jsx";
import AccountBlockedPage from "./features/auth/AccountBlockedPage.jsx";
import RoleHomePage from "./features/auth/RoleHomePage.jsx";
import ProductListingPage from "./features/catalog/ProductListingPage.jsx";
import ProductDetailPage from "./features/catalog/ProductDetailPage.jsx";
import CartPage from "./features/cart/CartPage.jsx";
import WishlistPage from "./features/wishlist/WishlistPage.jsx";
import OnboardingWizardPage from "./features/vendor-onboarding/OnboardingWizardPage.jsx";
import AdminReviewQueuePage from "./features/vendor-onboarding/AdminReviewQueuePage.jsx";
import AdminVendorDetailPage from "./features/vendor-onboarding/AdminVendorDetailPage.jsx";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/blocked" element={<AccountBlockedPage />} />
          <Route path="/home" element={<RoleHomePage />} />
          <Route path="/products" element={<ProductListingPage />} />
          <Route path="/products/:productId" element={<ProductDetailPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/wishlist" element={<WishlistPage />} />
          <Route path="/vendor/onboarding" element={<OnboardingWizardPage />} />
          <Route path="/admin/vendor-onboarding" element={<AdminReviewQueuePage />} />
          <Route path="/admin/vendor-onboarding/:vendorId" element={<AdminVendorDetailPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
