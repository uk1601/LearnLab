'use client';

import { useState } from 'react';
import { useAuth } from '@/components/providers/auth-provider';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertCircle, Eye, EyeOff } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface FormData {
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
  full_name: string;
}

export function RegisterForm() {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const { register, isLoading, error } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setValidationError(null);
  };

  const validateForm = () => {
    if (formData.password !== formData.confirmPassword) {
      setValidationError("Passwords don't match");
      return false;
    }
    if (formData.password.length < 8) {
      setValidationError("Password must be at least 8 characters long");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        full_name: formData.full_name,
      });
    } catch (err) {
      console.error('Registration error:', err);
    }
  };

  const renderFormField = (
    label: string,
    name: keyof FormData,
    type: string,
    placeholder: string,
    isPassword?: boolean
  ) => (
    <div className="space-y-2">
      <Label 
        htmlFor={name}
        className="text-foreground"
      >
        {label}
      </Label>
      <div className="relative">
        <Input
          id={name}
          name={name}
          type={isPassword ? (showPassword ? "text" : "password") : type}
          placeholder={placeholder}
          value={formData[name]}
          onChange={handleChange}
          required
          className="bg-background"
        />
        {isPassword && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? (
              <>
                <EyeOff className="h-4 w-4 mr-1" />
                Hide
              </>
            ) : (
              <>
                <Eye className="h-4 w-4 mr-1" />
                Show
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {(error || validationError) && (
        <Alert variant="destructive" className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error || validationError}</AlertDescription>
        </Alert>
      )}

      {renderFormField('Full Name', 'full_name', 'text', 'Enter your full name')}
      {renderFormField('Email', 'email', 'email', 'Enter your email')}
      {renderFormField('Username', 'username', 'text', 'Choose a username')}
      {renderFormField('Password', 'password', 'password', 'Create a password', true)}
      {renderFormField('Confirm Password', 'confirmPassword', 'password', 'Confirm your password', true)}

      <Button 
        type="submit" 
        className="btn-primary w-full hover-base hover-lift"
        size="lg"
        disabled={isLoading}
      >
        {isLoading ? 'Creating account...' : 'Create Account'}
      </Button>
    </form>
  );
}