import React, { useState, useRef, useEffect } from "react";
import { Menu, X, BellRing, Bell, Folder, Users, Clock, Plus, 
        Search, FilterIcon, House, MoreVertical, Settings, MessageCircle, Info, 
        Sparkles, UserPlus, LogOut, User } from "lucide-react";
import HomeComponent from "../Home";
import { handleLogout } from "../../../api/v1/Auth";
import { useNavigate } from "react-router-dom";

function SearchBar() {
  return (
    <div className="flex justify-center items-center w-full px-4">
      <div className="relative w-full max-w-lg md:max-w-2xl lg:max-w-3xl">
        <Search
          size={18}
          className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500"
        />
        <input
          type="text"
          placeholder="Search in mycloudy"
          className="w-full pl-10 pr-12 py-2 border border-gray-300 font-poppins rounded-3xl focus:outline-none focus:ring-2 focus:ring-[#1795DC] focus:border-transparent"
        />
        <FilterIcon
          size={34}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 cursor-pointer hover:bg-gray-200 rounded-2xl p-1.5"
        />
      </div>
    </div>
  );
}

function NotificationButton() {
  const [isHovered, setIsHovered] = useState(false);
  const [isClicked, setIsClicked] = useState(false);
  const [notifications, setNotifications] = useState([]);

  const handleClick = () => {
      setIsClicked((prev) => !prev);
  };

  return (
      <div className="relative">
          <button
              className="text-gray-600 hover:text-gray-800 mr-4"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              onClick={handleClick}
          >
              {isClicked ? <BellRing size={24} /> : isHovered ? <BellRing size={24} /> : <Bell size={24} />}
          </button>

          {isClicked && (
              <div className="absolute right-0 mt-4 w-80 bg-white shadow-lg rounded-lg p-4 z-10">
                  <h2 className="text-lg font-poppins font-medium text-gray-800 mb-4">Notifications</h2>
                  {notifications.length === 0 ? (
                      <p className="text-gray-600">No new notifications</p>
                  ) : (
                      notifications.map((notification) => (
                          <div key={notification.id} className="flex items-center p-2 rounded-lg hover:bg-gray-100">
                              <p className="text-gray-800">{notification.message}</p>
                          </div>
                      ))
                  )}
              </div>
          )}
      </div>
  );
}

function SidebarMenu({ activeItemSideBar, setActiveItemSideBar }) {

  const menuItems = [
      { id: "Home", name: "Home", icon: House },
      { id: "My Files", name: "My Files", icon: Folder },
      { id: "Shared", name: "Shared", icon: Users },
      { id: "Recent", name: "Recent", icon: Clock },
  ];

  return (

    <nav className="space-y-2 font-poppins mt-2">
      {menuItems.map(({ id, name, icon: Icon }) => (
        <a
          key={id}
          href="#"
          className={`group flex items-center p-3 rounded-3xl transition ${
            activeItemSideBar === id ? "bg-gray-200" : "hover:bg-gray-200"
          }`}
          onClick={(e) => {
            e.preventDefault();
            setActiveItemSideBar(id);
          }}
        >
          <Icon
            size={20}
            strokeWidth={activeItemSideBar === id ? 3 : 2} // Thicker when active
            className="mx-3 text-gray-700 transition-all group-hover:stroke-[3]"
          />
          {name}
        </a>
      ))}
    </nav>
  );
}

function SidebarMenuBottom({ activeItemSideBar, setActiveItemSideBar }) {


  const menuItems = [
      { id: "Settings", name: "Settings", icon: Settings },
      { id: "About", name: "About", icon: Info },
      { id: "Feedback", name: "Feedback", icon: MessageCircle },
  ];

  return (

    <nav className="space-y-2 font-poppins mt-2">
      {menuItems.map(({ id, name, icon: Icon }) => (
        <a
          key={id}
          href="#"
          className={`group flex items-center p-3 rounded-3xl transition ${
            activeItemSideBar === id ? "bg-gray-200" : "hover:bg-gray-200"
          }`}
          onClick={(e) => {
            e.preventDefault();
            setActiveItemSideBar(id);
          }}
        >
          <Icon
            size={20}
            strokeWidth={activeItemSideBar === id ? 3 : 2} // Thicker when active
            className="mx-3 text-gray-700 transition-all group-hover:stroke-[3]"
          />
          {name}
        </a>
      ))}
    </nav>
  );
}


function SidebarMenuMobile({ activeItemSideBar, setActiveItemSideBar }) {
  const menuItems = [
    { id: "Home", name: "Home", icon: House },
    { id: "My Files", name: "My Files", icon: Folder },
    { id: "Shared", name: "Shared", icon: Users },
    { id: "Recent", name: "Recent", icon: Clock },
  ];

  return (
    <nav className="space-y-2 font-poppins">
      {menuItems.map(({ id, name, icon: Icon }) => (
        <a
          key={id}
          href="#"
          className={`group flex items-center p-3 rounded-3xl transition ${
            activeItemSideBar === id ? "bg-gray-200" : "hover:bg-gray-200"
          }`}
          onClick={(e) => {
            e.preventDefault();
            setActiveItemSideBar(id);
          }}
        >
          <Icon
            size={20}
            strokeWidth={activeItemSideBar === id ? 3 : 2} // Thicker when active
            className="mx-3 text-gray-700 transition-all group-hover:stroke-[3]"
          />
          {name}
        </a>
      ))}
    </nav>
  );
}

function SidebarMenuBottomMobile({ activeItemSideBar, setActiveItemSideBar }) {
  const menuItems = [
    { id: "Settings", name: "Settings", icon: Settings },
    { id: "About", name: "About", icon: Info },
    { id: "Feedback", name: "Feedback", icon: MessageCircle },
  ];

  return (
    <nav className="space-y-2 font-poppins">
      {menuItems.map(({ id, name, icon: Icon }) => (
        <a
          key={id}
          href="#"
          className={`group flex items-center p-3 rounded-3xl transition ${
            activeItemSideBar === id ? "bg-gray-200" : "hover:bg-gray-200"
          }`}
          onClick={(e) => {
            e.preventDefault();
            setActiveItemSideBar(id);
          }}
        >
          <Icon
            size={20}
            strokeWidth={activeItemSideBar === id ? 3 : 2} // Thicker when active
            className="mx-3 text-gray-700 transition-all group-hover:stroke-[3]"
          />
          {name}
        </a>
      ))}
    </nav>
  );
}


function Index() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeItemSideBar, setActiveItemSideBar] = useState("Home");
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsMenuOpen(false);
      }
    }

    if (isMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    } else {
      document.removeEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isMenuOpen]);

  const name = sessionStorage.getItem("name");
  const email = sessionStorage.getItem("email");

  return (
    <div className="flex h-screen bg-[#FAF9F6]">
      {/* Sidebar */}
      <aside className="hidden lg:flex flex-col w-60 bg-[#FAF9F6] p-4 space-y-4 shadow-lg fixed left-0 top-0 h-full">
          <div className="flex justify-center items-center">
              <h1 className="text-3xl font-medium font-monoton text-[#1795DC]">mycloudy</h1>
          </div>

          {/* New File Button */}
          <div className="pt-8">
            <button className="flex items-center justify-center font-poppins font-medium w-2/3 h-12 p-2 
            rounded-4xl bg-[#FAF9F6] text-[#1795DC] text-xl border-1 border-black hover:bg-[#1795DC] hover:text-white hover:border-black-500">
                <Plus size={22} className="mr-2" />
                New
            </button>
          </div>


          <SidebarMenu
            activeItemSideBar={activeItemSideBar}
            setActiveItemSideBar={setActiveItemSideBar}
          />
          
          {/* Line */}
          <div className="flex items-center w-full">
            <div className="flex-1 h-px bg-gray-300"></div>
          </div>

          {/* Menu Options */}
          <SidebarMenuBottom
            activeItemSideBar={activeItemSideBar}
            setActiveItemSideBar={setActiveItemSideBar}
          />

          {/* Push to Bottom */}
          <div className="mt-auto space-y-5">

            {/* Update Notification */}
            {/* <div className="bg-white p-4 rounded-lg shadow-md border border-gray-300 h-36 flex flex-col justify-center">
              <Sparkles className="text-black w-9 h-9" />
              <p className="text-sm font-semibold text-black">New Update Available</p>
              <p className="text-xs text-gray-500 mt-1">A new update has arrived. Click below to update now.</p>
              <button className="mt-2 w-full bg-black text-white text-sm py-2 rounded-lg hover:bg-gray-800 flex items-center justify-center space-x-2">
                
                <span>Update Now</span>
              </button>
            </div> */}

            <hr className="border-t border-gray-300 my-2" />
          <div className="relative">
            {/* User Profile */}
            <div className="flex items-center justify-between p-1.5 rounded-lg transition">
              {/* User Avatar */}
              <img className="w-10 h-10 rounded-full" src="https://avatar.iran.liara.run/public/42" alt="User Avatar" />

              {/* User Info */}
              <div className="ml-3 flex-1 overflow-hidden">
                <p className="text-gray-800 font-medium font-poppins truncate">{name}</p>
                <p className="text-gray-500 text-sm truncate">{email}</p>
              </div>

              {/* Three-Dot Menu */}
              <MoreVertical
                className="text-gray-500 w-6 h-6 p-0.5 rounded-2xl hover:bg-gray-200 cursor-pointer"
                onClick={(e) => {
                  e.stopPropagation(); // Prevents unwanted reopens
                  setIsMenuOpen((prev) => !prev);
                }}
              />
            </div>

            {/* Dropdown Menu */}
            {isMenuOpen && (
              <div ref={menuRef} className="absolute right-1 bottom-14 w-40 bg-white shadow-lg rounded-xl overflow-hidden z-10">
                <button
                  onClick={() => alert("Profile Clicked")}
                  className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 w-full transition-all"
                >
                  <User size={16} className="mr-2" />
                  Profile
                </button>
                <button
                  onClick={() => handleLogout(navigate)}
                  className="flex items-center px-4 py-2 text-gray-700 hover:bg-[#EF4444] hover:text-white w-full transition-all"
                >
                  <LogOut size={16} className="mr-2" />
                  Logout
                </button>
              </div>
            )}
            </div>
          </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col max-w-full lg:ml-60 pt-[4rem]">
          {/* Navbar */}
          <header className="bg-[#FAF9F6] p-4 flex justify-between items-center fixed top-0 left-0 lg:left-60 right-0 z-10">
              {/* Mobile Menu Button */}
              <button className="lg:hidden" onClick={() => setIsOpen(!isOpen)}>
                  {isOpen ? <X size={24} /> : <Menu size={24} />}
              </button>

              {/* Search Bar */}
              <SearchBar />

              {/* Bell Icon (Notifications) */}
              <NotificationButton />
          </header>

          <div className="flex items-center w-full my-2.5 fixed top-[4rem] left-0 right-0 z-0">
            <div className="flex-1 h-px bg-gray-300"></div>
          </div>

        {/* Sidebar for mobile */}
        {isOpen && (
          <div className="fixed inset-0 bg-[#0000007c] bg-opacity-50 lg:hidden z-20" onClick={() => setIsOpen(false)}>
            <aside className="absolute left-0 top-0 h-full w-60 bg-white shadow-lg p-4 space-y-4 rounded-r-2xl flex flex-col">
              {/* Close Button */}
              <button className="mb-4" onClick={() => setIsOpen(false)}>
                <X size={24} />
              </button>

              {/* New Button */}
              <button className="flex items-center justify-center ml-2 font-poppins font-medium w-2/4 h-10 p-2
                rounded-4xl bg-[#FAF9F6] text-[#21a4f0] text-md border-1 border-black">
                <Plus size={18} className="mr-2" />
                New
              </button>


              {/* Sidebar Menu */}
              <SidebarMenuMobile activeItemSideBar={activeItemSideBar} setActiveItemSideBar={setActiveItemSideBar} />

              {/* Divider */}
              <div className="flex items-center w-full mb-4">
                <div className="flex-1 h-px bg-gray-300"></div>
              </div>

              {/* Sidebar Menu Bottom */}
              <SidebarMenuBottomMobile activeItemSideBar={activeItemSideBar} setActiveItemSideBar={setActiveItemSideBar} />

              {/* Divider */}
              <div className="flex-1"></div> {/* Push content above */}
              <div className="relative">
              <div className="border-t border-gray-300 my-2"></div>

              {/* User Profile - Stays at the bottom */}
              <div className="p-1.5 rounded-lg transition flex items-center justify-between">
                {/* User Avatar */}
                <img className="w-10 h-10 rounded-full" src="https://avatar.iran.liara.run/public/42" alt="User Avatar" />

                {/* User Info */}
                <div className="ml-3 flex-1 overflow-hidden">
                  <p className="text-gray-800 font-medium font-poppins truncate">{name}</p>
                  <p className="text-gray-500 text-sm truncate">{email}</p>
                </div>

                {/* Three-Dot Menu */}
                <MoreVertical className="text-gray-500 w-6 h-6 p-0.5 rounded-2xl cursor-pointer hover:bg-gray-200 " 
                onClick={(e) => {
                  e.stopPropagation(); // Prevents unwanted reopens
                  setIsMenuOpen((prev) => !prev);
                }}/>
              </div>

              {/* Dropdown Menu */}
              {isMenuOpen && (
                <div ref={menuRef} className="absolute right-1 bottom-14 w-40 bg-white shadow-lg rounded-xl overflow-hidden z-10">
                  <button
                    onClick={() => alert("Profile Clicked")}
                    className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 w-full transition-all"
                  >
                    <User size={16} className="mr-2" />
                    Profile
                  </button>
                  <button
                    onClick={() => handleLogout(navigate)}
                    className="flex items-center px-4 py-2 text-gray-700 hover:bg-[#EF4444] hover:text-white w-full transition-all"
                  >
                    <LogOut size={16} className="mr-2" />
                    Logout
                  </button>
                </div>
              )}
              </div>
            </aside>
          </div>
        )}

        <div className="flex items-center w-full mb-4">
          <div className="flex-1 h-px bg-gray-300"></div>
        </div>

        {/* Main Content */}
        <HomeComponent />


      </div>
    </div>
  );
}

export default Index;