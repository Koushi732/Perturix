import React from 'react';
import { PageContainer } from '../components/common/PageContainer';
import { BookOpen, Layers, Shield, Cpu, ExternalLink } from 'lucide-react';

export default function AboutPage() {
  return (
    <PageContainer title="About Perturix" description="Computer Vision & Adversarial Machine Learning Research Framework">
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-card p-6 md:col-span-2">
          <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
            <BookOpen className="w-5 h-5 text-primary-500 mr-2" aria-hidden="true" />
            Problem Statement
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed mb-4">
            With the rapid advancement of generative AI and facial recognition models, unauthorized image harvesting and manipulation have become critical privacy concerns. Users uploading personal photos to the internet have virtually no technical defense against these models extracting their biometric data or utilizing their likeness.
          </p>
          <p className="text-sm text-slate-300 leading-relaxed">
            Perturix aims to solve this by applying <strong className="text-primary-400 font-medium">adversarial machine learning</strong>—injecting imperceptible, calculated noise (perturbations) into images. This noise is mathematically designed to maximize the loss function of target neural networks, effectively "blinding" them and causing misclassification or failure in feature extraction, while remaining invisible to the human eye.
          </p>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
            <Cpu className="w-5 h-5 text-accent-500 mr-2" aria-hidden="true" />
            Technology Stack
          </h3>
          <ul className="space-y-3 text-sm text-slate-300">
            <li className="flex justify-between border-b border-black/5 pb-2">
              <span>Frontend</span>
              <span className="text-slate-900 dark:text-white">React, Vite, Tailwind v4</span>
            </li>
            <li className="flex justify-between border-b border-black/5 pb-2">
              <span>Backend Core</span>
              <span className="text-slate-900 dark:text-white">FastAPI, Python 3.10</span>
            </li>
            <li className="flex justify-between border-b border-black/5 pb-2">
              <span>ML Framework</span>
              <span className="text-slate-900 dark:text-white">PyTorch, TorchVision</span>
            </li>
            <li className="flex justify-between border-b border-black/5 pb-2">
              <span>Image Processing</span>
              <span className="text-slate-900 dark:text-white">Pillow, NumPy</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="mb-8">
        <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
          <Layers className="w-5 h-5 text-primary-500 mr-2" aria-hidden="true" />
          Architecture & Workflow
        </h3>
        <div className="glass-panel p-2 flex flex-col items-center justify-center border border-black/5 bg-slate-50 dark:bg-dark-900/50 min-h-[300px] overflow-hidden rounded-xl">
          <img src="/architecture.png" alt="Perturix Architecture Diagram" className="w-full h-auto object-cover rounded-lg" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
            <Shield className="w-5 h-5 text-emerald-500 mr-2" aria-hidden="true" />
            Future Work
          </h3>
          <ul className="space-y-2 text-sm text-slate-300 list-disc list-inside">
            <li>Implementation of ProtectionNet architecture.</li>
            <li>Ensemble adversarial attacks for transferability.</li>
            <li>Real-time browser-based WebGL perturbation (WASM).</li>
            <li>Docker containerization and Redis queueing.</li>
          </ul>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
            <ExternalLink className="w-5 h-5 text-slate-300 mr-2" aria-hidden="true" />
            References
          </h3>
          <ul className="space-y-3 text-sm text-slate-300">
            <li className="hover:text-primary-400 cursor-pointer transition-colors">
              [1] Explaining and Harnessing Adversarial Examples (Goodfellow et al.)
            </li>
            <li className="hover:text-primary-400 cursor-pointer transition-colors">
              [2] Towards Deep Learning Models Resistant to Adversarial Attacks (Madry et al.)
            </li>
            <li className="hover:text-primary-400 cursor-pointer transition-colors">
              [3] Fawkes: Protecting Privacy against Unauthorized Deep Learning Models
            </li>
          </ul>
        </div>
      </div>

    </PageContainer>
  );
}
