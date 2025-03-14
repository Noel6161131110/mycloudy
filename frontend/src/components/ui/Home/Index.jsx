import React from 'react'
import { File, Image, Video, Code, Users, Calendar, Folder, ChevronDown } from "lucide-react";

function Index() {
    const recentFiles = [
        { id: 1, name: "Project Report.pdf", type: "Document" },
        { id: 2, name: "Design Mockup.png", type: "Image" },
        { id: 3, name: "Meeting Notes.docx", type: "Document" },
        { id: 4, name: "Code Snippet.js", type: "Code" },
        { id: 5, name: "Midhunam.mp4", type: "Video" },
        { id: 6, name: "Project Plan.pdf", type: "Document" },
        { id: 7, name: "Project Report.pdf", type: "Document" },
        { id: 8, name: "Design Mockup.png", type: "Image" },
        { id: 9, name: "Meeting Notes.docx", type: "Document" },
        { id: 10, name: "Code Snippet.js", type: "Code" },
        { id: 11, name: "Midhunam.mp4", type: "Video" },
        { id: 12, name: "Project Plan.pdf", type: "Document" },
    ];

    const filters = [
        { id: 1, name: "Type", icon: File },
        { id: 2, name: "People", icon: Users },
        { id: 3, name: "Modified", icon: Calendar },
        { id: 4, name: "Location", icon: Folder },
    ];
    
    const iconMap = {
        Document: File,
        Image: Image,
        Video: Video,
        Code: Code,
    };
    
    return (
        <>

            <div className="max-w-full border-none">
                {/* Filter Section */}

                <div className="p-4 w-full border-none">
                        <div className="overflow-x-auto no-scrollbar">
                            <div className="flex whitespace-nowrap gap-2 min-w-min">
                                {filters.map(({ id, name, icon: Icon }) => (
                                    <button
                                        key={id}
                                        className="flex items-center space-x-2 px-4 py-2 rounded-full bg-gray-100 hover:bg-gray-200 transition flex-shrink-0"
                                    >
                                        <Icon size={18} className="text-gray-600" />
                                        <span className="text-gray-800 text-sm font-poppins font-medium">{name}</span>
                                        <ChevronDown size={16} className="text-gray-600" />
                                    </button>
                                ))}
                            </div>
                        </div>
                </div>


                {/* Recent Files Section */}
                <div className="p-4 max-w-full">
                    <div className="flex items-center w-full mb-4">
                        <h2 className="text-2xl font-poppins text-gray-800 whitespace-nowrap pr-4">Recent Files</h2>
                        <div className="flex-1 h-px bg-gray-300"></div>
                    </div>
                    
                    <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6 w-full">
                        {recentFiles.map((file) => {
                            const IconComponent = iconMap[file.type] || File; // Default to File icon if type not found
                            return (
                                <div
                                    key={file.id}
                                    className="w-full max-w-full aspect-square bg-white shadow rounded-xl flex items-center justify-center p-2"
                                >
                                    <div className="w-full h-full bg-gray-100 rounded-md flex flex-col items-center justify-center p-4">
                                        <IconComponent size={40} className="text-gray-600" />
                                        <p className="mt-2 text-gray-800 text-sm font-medium font-poppins text-center truncate w-full">
                                            {file.name}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </>
    )
}

export default Index