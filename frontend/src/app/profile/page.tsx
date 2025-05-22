'use client';

import { UserProfile } from '@/components/auth/user-profile';
import { ProtectedRoute } from '@/lib/protected-route';

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <div className="container max-w-5xl mx-auto py-12 px-4">
        <div className="flex flex-col items-center">
          <h1 className="text-3xl font-bold mb-8">My Profile</h1>
          <UserProfile />
        </div>
      </div>
    </ProtectedRoute>
  );
} 