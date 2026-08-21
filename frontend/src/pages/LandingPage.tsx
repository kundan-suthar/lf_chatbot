import { MessageCircle, ShieldCheck, UserRound } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const customerProfiles = [
  { customer_id: "cust-001", name: "Rahul Sharma" },
  { customer_id: "cust-002", name: "Priya Mehta" },
  { customer_id: "cust-003", name: "Amit Verma" },
  { customer_id: "cust-004", name: "Neha Gupta" },
  { customer_id: "cust-005", name: "Vikram Singh" },
];

type CustomerProfile = (typeof customerProfiles)[number];

const getInitials = (name: string) =>
  name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2);

const LandingPage = () => {
  const [selectedCustomer, setSelectedCustomer] =
    useState<CustomerProfile | null>(null);
  const navigate = useNavigate();

  const startConversation = () => {
    if (selectedCustomer) {
      navigate(`/chat?customer_id=${selectedCustomer.customer_id}`);
    }
  };

  return (
    <main className="landing-page">
      <section className="landing-shell" aria-labelledby="landing-title">
        <header className="landing-header">
          <img className="site-logo" src="/SiteLogo.svg" alt="Loanfront" />
        </header>

        <div className="landing-intro">
          <h1 id="landing-title">Loan Assistant</h1>
          <p>AI-powered loan guidance</p>
        </div>

        <div className="bot-stage" aria-hidden="true">
          <img src="/LandingBot.png" alt="" />
        </div>

        <div className="landing-copy">
          <h2>Get Started</h2>
          <p>Select a user profile to begin your conversation</p>
        </div>

        <div className="profile-field">
          <label htmlFor="customer-profile">Select User Profile</label>
          <div className="select-wrap">
            <Select
              value={selectedCustomer?.customer_id ?? null}
              onValueChange={(customerId) =>
                setSelectedCustomer(
                  customerProfiles.find(
                    (customer) => customer.customer_id === customerId,
                  ) ?? null,
                )
              }
            >
              <SelectTrigger
                id="customer-profile"
                className={`profile-select-trigger${selectedCustomer ? "" : " placeholder"}`}
              >
                <UserRound
                  aria-hidden="true"
                  className="profile-trigger-icon"
                />
                <SelectValue placeholder="Choose a profile..." />
              </SelectTrigger>
              <SelectContent className="profile-options">
                {customerProfiles.map((customer) => (
                  <SelectItem
                    key={customer.customer_id}
                    value={customer.customer_id}
                    className="profile-option-item"
                  >
                    <span className="profile-avatar">
                      {getInitials(customer.name)}
                    </span>
                    <span className="profile-option-copy">
                      <strong>{customer.name}</strong>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <button
          className="start-button"
          type="button"
          disabled={!selectedCustomer}
          onClick={startConversation}
        >
          <MessageCircle aria-hidden="true" />
          Start Conversation
        </button>

        <p className="demo-note">
          <ShieldCheck aria-hidden="true" />
          This is a demo environment — no real data is used
        </p>
      </section>
    </main>
  );
};

export default LandingPage;
