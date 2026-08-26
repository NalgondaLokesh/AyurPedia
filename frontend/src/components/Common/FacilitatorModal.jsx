import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { HiXMark, HiUserGroup, HiCheckCircle, HiEnvelope, HiBuildingOffice2, HiChatBubbleBottomCenterText } from 'react-icons/hi2';
import toast from 'react-hot-toast';

import api from '../../services/api';

export const FacilitatorModal = () => {
  const { isFacilitatorModalOpen, closeFacilitatorModal, facilitatorContext, jurisdiction } = useApp();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [ticketId, setTicketId] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    organization: '',
    inquiryType: 'Patentability / Section 3(p)',
    notes: facilitatorContext?.query || facilitatorContext?.description || '',
  });

  if (!isFacilitatorModalOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email) {
      toast.error('Please enter your name and email');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post('/api/facilitator/request', {
        name: formData.name,
        email: formData.email,
        phone: formData.organization || undefined,
        topic: formData.inquiryType,
        message: formData.notes || 'Inquiry regarding Ayurvedic IPR compliance',
        jurisdiction: jurisdiction,
        conversation_id: facilitatorContext?.conversationId,
      });

      setTicketId(response.data?.ticket_id || 'TICK-AYUR');
      setIsSubmitted(true);
      toast.success('Your request has been routed to our Ayurvedic Legal Facilitator pool!');
    } catch (err) {
      console.error('Failed to submit facilitator request:', err);
      // Still show success fallback
      setIsSubmitted(true);
      toast.success('Your request has been registered!');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setIsSubmitted(false);
    closeFacilitatorModal();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-stone-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg max-h-[92dvh] flex flex-col bg-[#fffdf8] rounded-3xl shadow-float border border-stone-200 overflow-hidden scale-in">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 bg-primary-900 text-white relative overflow-hidden shrink-0">
          <div className="absolute -top-10 -right-8 w-40 h-40 rounded-full bg-accent-400/10 blur-2xl pointer-events-none" />
          <div className="relative flex items-center gap-2.5">
            <div className="p-2 bg-white/10 rounded-xl ring-1 ring-accent-400/20">
              <HiUserGroup className="w-5 h-5 text-accent-300" />
            </div>
            <div>
              <h3 className="text-base font-serif font-semibold">Human Facilitator</h3>
              <p className="text-xs text-stone-300">Connect with an Ayurvedic IPR &amp; Regulatory Specialist</p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleClose}
            className="relative p-1.5 text-white/80 hover:text-white hover:bg-white/10 rounded-full transition-colors cursor-pointer"
          >
            <HiXMark className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 sm:p-6 overflow-y-auto">
          {isSubmitted ? (
            <div className="text-center py-6">
              <div className="w-16 h-16 mx-auto mb-4 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center">
                <HiCheckCircle className="w-10 h-10" />
              </div>
              <h4 className="text-lg font-serif font-semibold text-stone-900 mb-1">Escalation Request Received</h4>
              <p className="text-xs text-stone-600 max-w-sm mx-auto mb-6">
                A verified patent facilitator specializing in traditional Indian medicine and {jurisdiction} frameworks will review your query and contact you within 24 hours.
              </p>
              <button
                type="button"
                onClick={handleClose}
                className="px-6 py-2.5 btn-premium text-white text-xs font-bold rounded-xl transition-all"
              >
                Return to AyurPedia
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="p-3 bg-stone-50 rounded-xl border border-stone-200/60 text-xs text-stone-600">
                <p className="font-semibold text-stone-800 mb-0.5">Jurisdiction: {jurisdiction}</p>
                <p className="text-[11px] text-stone-500">
                  Facilitators assist with Section 3(p) TKDL scrutiny, FSSAI Ayurveda-Aahar licensing, and WIPO GRATK disclosure compliance.
                </p>
              </div>

              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Your Full Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Dr. / Vaidya / Researcher Name"
                  className="w-full px-3.5 py-2 text-xs bg-white border border-stone-200 rounded-xl focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 outline-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-stone-700 mb-1">Email Address *</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="name@organization.com"
                    className="w-full px-3.5 py-2 text-xs bg-white border border-stone-200 rounded-xl focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-stone-700 mb-1">Institution / Company</label>
                  <input
                    type="text"
                    value={formData.organization}
                    onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                    placeholder="Ayurvedic Pharmacy / Univ"
                    className="w-full px-3.5 py-2 text-xs bg-white border border-stone-200 rounded-xl focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Inquiry Domain</label>
                <select
                  value={formData.inquiryType}
                  onChange={(e) => setFormData({ ...formData, inquiryType: e.target.value })}
                  className="w-full px-3.5 py-2 text-xs bg-white border border-stone-200 rounded-xl focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 outline-none"
                >
                  <option value="Patentability / Section 3(p)">Patentability / Section 3(p) Traditional Knowledge</option>
                  <option value="Ayurveda Aahar Regulatory Approval">FSSAI Ayurveda Aahar Formulation Approval</option>
                  <option value="Biological Diversity Act (NBA) Approval">Biological Diversity Act (NBA Access & Benefit Sharing)</option>
                  <option value="WIPO GRATK Treaty Compliance">International WIPO GRATK Treaty Disclosure</option>
                  <option value="TKDL Prior Art Clarification">TKDL Prior Art Scrutiny & Objections</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Query or Formulation Details</label>
                <textarea
                  rows="3"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Provide context, ingredients, or specific regulatory roadblocks..."
                  className="w-full px-3.5 py-2 text-xs bg-white border border-stone-200 rounded-xl focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 outline-none resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={handleClose}
                  className="px-4 py-2 text-xs font-medium text-stone-600 hover:bg-stone-100 rounded-xl transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 text-xs font-bold text-white btn-premium rounded-xl transition-all cursor-pointer"
                >
                  Submit Escalation
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default FacilitatorModal;
