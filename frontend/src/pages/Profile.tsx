import { useState, useMemo, useEffect } from "react";
import { motion } from "framer-motion";
import { Particles } from "@/components/background/Particles";
import { User, FileText, Upload, ChevronDown, GraduationCap, Calendar as CalendarIcon, Award, Hash } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import type { Course } from "@/types";

export function Profile() {
  const storeCourses = useAppStore((s) => s.courses);
  const [selectedSemester, setSelectedSemester] = useState("");

  const getSemesterStr = (course: Course) => {
    if (!course.start_at) return "Unknown Semester";
    const d = new Date(course.start_at);
    const year = d.getFullYear();
    const month = d.getMonth(); // 0 is Jan
    if (month < 5) return `Spring ${year}`;
    if (month < 8) return `Summer ${year}`;
    return `Fall ${year}`;
  };

  const getGrade = (progress: number) => {
    if (progress === 0) return "TBD";
    if (progress >= 97) return "A+";
    if (progress >= 93) return "A";
    if (progress >= 90) return "A-";
    if (progress >= 87) return "B+";
    if (progress >= 83) return "B";
    if (progress >= 80) return "B-";
    if (progress >= 77) return "C+";
    if (progress >= 73) return "C";
    if (progress >= 70) return "C-";
    if (progress >= 65) return "D+";
    if (progress >= 60) return "D";
    return "F";
  };

  const courseData = useMemo(() => {
    const data: Record<string, Course[]> = {};
    storeCourses.forEach(c => {
      const sem = getSemesterStr(c);
      if (!data[sem]) data[sem] = [];
      data[sem].push(c);
    });
    return data;
  }, [storeCourses]);

  const semesters = useMemo(() => {
    return Object.keys(courseData).sort((a, b) => {
      if (a === "Unknown Semester") return 1;
      if (b === "Unknown Semester") return -1;
      const [seasonA, yearA] = a.split(" ");
      const [seasonB, yearB] = b.split(" ");
      if (yearA !== yearB) return parseInt(yearB) - parseInt(yearA);
      const order: Record<string, number> = { "Fall": 3, "Summer": 2, "Spring": 1 };
      return order[seasonB] - order[seasonA];
    });
  }, [courseData]);

  useEffect(() => {
    if ((!selectedSemester || !semesters.includes(selectedSemester)) && semesters.length > 0) {
      setSelectedSemester(semesters[0]);
    }
  }, [semesters, selectedSemester]);

  const currentCourses = courseData[selectedSemester] || [];

  return (
    <div className="h-full relative overflow-hidden aether-hub-bg">
      <div className="absolute inset-0 z-0 pointer-events-none aether-mesh-overlay" />
      <Particles
        className="z-[1]"
        quantity={100}
        staticity={55}
        ease={60}
        size={0.4}
        color="#ffffff"
      />

      <div className="relative z-10 flex flex-col h-full overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.32, 0.72, 0, 1] }}
          className="mx-auto px-8 relative z-20 max-w-5xl w-full pt-16 pb-24"
        >
          {/* Header */}
          <div className="flex items-center gap-4 mb-10">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#FF6B6B] to-[#FF5252] flex items-center justify-center shrink-0 glow-indigo border border-white/10">
              <User size={32} className="text-white" />
            </div>
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div className="w-1.5 h-1.5 rounded-full bg-[#FF6B6B] animate-pulse" />
                <span className="text-[10px] font-mono tracking-[0.2em] text-white/30 uppercase">
                  Student Profile
                </span>
              </div>
              <h1 className="text-3xl font-medium text-white/95 tracking-tight">Jane Doe</h1>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Stats Cards */}
            <div className="command-brief-card rounded-2xl p-6 flex flex-col transition-all hover:bg-white/[0.04]">
              <div className="flex items-center gap-3 mb-4 text-white/40">
                <Hash size={18} />
                <span className="text-xs font-mono tracking-wider uppercase">University ID</span>
              </div>
              <span className="text-2xl font-medium text-white/90">123456789</span>
            </div>

            <div className="command-brief-card rounded-2xl p-6 flex flex-col transition-all hover:bg-white/[0.04]">
              <div className="flex items-center gap-3 mb-4 text-white/40">
                <GraduationCap size={18} />
                <span className="text-xs font-mono tracking-wider uppercase">Academic Year</span>
              </div>
              <span className="text-xl font-medium text-white/90">Junior</span>
              <span className="text-sm text-white/40 mt-1">Second Semester</span>
            </div>

            <div className="command-brief-card rounded-2xl p-6 flex flex-col transition-all hover:bg-white/[0.04]">
              <div className="flex items-center gap-3 mb-4 text-white/40">
                <Award size={18} />
                <span className="text-xs font-mono tracking-wider uppercase">Cumulative GPA</span>
              </div>
              <span className="text-2xl font-medium text-white/90 text-[#FF6B6B]">3.84</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Academic History */}
            <div className="lg:col-span-2 space-y-6">
              <div className="command-brief-card rounded-2xl p-8">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
                  <div className="flex items-center gap-3">
                    <CalendarIcon size={20} className="text-[#FF6B6B]" />
                    <h2 className="text-lg font-medium text-white/90">Academic History</h2>
                  </div>
                  
                  {semesters.length > 0 && (
                    <div className="relative">
                      <select
                        value={selectedSemester}
                        onChange={(e) => setSelectedSemester(e.target.value)}
                        className="appearance-none bg-white/[0.03] border border-white/[0.08] hover:border-white/[0.15] rounded-xl px-4 py-2 pr-10 text-sm text-white/80 focus:outline-none focus:border-white/20 transition-all w-full sm:w-auto"
                      >
                        {semesters.map(s => (
                          <option key={s} value={s} className="bg-[#0d0a0a] text-white/90">{s}</option>
                        ))}
                      </select>
                      <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 pointer-events-none" />
                    </div>
                  )}
                </div>

                <div className="space-y-3">
                  {currentCourses.length === 0 ? (
                    <p className="text-sm text-white/40 italic">No courses found for this semester.</p>
                  ) : (
                    currentCourses.map((course, i) => {
                      const grade = getGrade(course.progress);
                      return (
                        <motion.div
                          key={`${course.id}-${selectedSemester}`}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1, duration: 0.4 }}
                          className="flex items-center justify-between p-4 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.06] hover:border-white/[0.08] transition-all group"
                        >
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-white/[0.03] border border-white/[0.06] flex items-center justify-center shrink-0 group-hover:bg-white/[0.05] transition-colors">
                              <span className="text-xs font-mono text-white/60">{course.course_code.replace(/\D/g,'')}</span>
                            </div>
                            <div>
                              <h3 className="text-white/90 font-medium group-hover:text-white transition-colors">{course.course_code}</h3>
                              <p className="text-sm text-white/40 group-hover:text-white/50 transition-colors">{course.name}</p>
                            </div>
                          </div>
                          <div className={`flex items-center justify-center w-12 h-10 rounded-full bg-[#FF6B6B]/10 font-medium border border-[#FF6B6B]/20 shadow-[0_0_10px_rgba(255,107,107,0.1)] ${grade === 'TBD' ? 'text-white/40 text-xs' : 'text-[#FF6B6B]'}`}>
                            {grade}
                          </div>
                        </motion.div>
                      );
                    })
                  )}
                </div>
              </div>
            </div>

            {/* Documents */}
            <div className="space-y-6">
              <div className="command-brief-card rounded-2xl p-8">
                <div className="flex items-center gap-3 mb-6">
                  <FileText size={20} className="text-[#FF6B6B]" />
                  <h2 className="text-lg font-medium text-white/90">Documents</h2>
                </div>

                <div className="space-y-4">
                  {/* Uploaded Document */}
                  <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-start gap-4 hover:bg-white/[0.05] transition-all cursor-pointer group">
                    <div className="p-2.5 rounded-lg bg-[#FF6B6B]/10 text-[#FF6B6B] group-hover:scale-110 transition-transform">
                      <FileText size={20} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-white/90 truncate group-hover:text-white transition-colors">Transcript_Current.pdf</h4>
                      <p className="text-xs text-white/40 mt-1">Uploaded Apr 12, 2026 • 2.4 MB</p>
                    </div>
                  </div>

                  {/* Upload Button */}
                  <button className="w-full py-5 rounded-xl border border-dashed border-white/10 hover:border-[#FF6B6B]/50 hover:bg-[#FF6B6B]/5 transition-all text-sm text-white/60 flex flex-col items-center justify-center gap-2.5 group">
                    <div className="p-2 rounded-full bg-white/[0.02] group-hover:bg-[#FF6B6B]/10 transition-colors">
                      <Upload size={18} className="text-white/40 group-hover:text-[#FF6B6B] transition-colors" />
                    </div>
                    <span>Upload Unofficial Transcript</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
