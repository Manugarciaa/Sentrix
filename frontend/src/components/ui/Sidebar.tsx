import React, { useState, createContext, useContext } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { ChevronRight } from 'lucide-react'

interface SidebarContextProps {
  open: boolean
  setOpen: React.Dispatch<React.SetStateAction<boolean>>
  animate: boolean
}

const SidebarContext = createContext<SidebarContextProps | undefined>(undefined)

export const useSidebar = () => {
  const context = useContext(SidebarContext)
  if (!context) {
    throw new Error('useSidebar must be used within a SidebarProvider')
  }
  return context
}

export const SidebarProvider = ({
  children,
  open: openProp,
  setOpen: setOpenProp,
  animate = true,
}: {
  children: React.ReactNode
  open?: boolean
  setOpen?: React.Dispatch<React.SetStateAction<boolean>>
  animate?: boolean
}) => {
  const [openState, setOpenState] = useState(false)

  const open = openProp !== undefined ? openProp : openState
  const setOpen = setOpenProp !== undefined ? setOpenProp : setOpenState

  return (
    <SidebarContext.Provider value={{ open, setOpen, animate }}>
      {children}
    </SidebarContext.Provider>
  )
}

export const Sidebar = ({
  children,
  open,
  setOpen,
  animate,
}: {
  children: React.ReactNode
  open?: boolean
  setOpen?: React.Dispatch<React.SetStateAction<boolean>>
  animate?: boolean
}) => {
  return (
    <SidebarProvider open={open} setOpen={setOpen} animate={animate}>
      {children}
    </SidebarProvider>
  )
}

export const SidebarBody = (props: React.ComponentProps<typeof motion.div>) => {
  return (
    <>
      <DesktopSidebar {...props} />
      <MobileSidebar {...(props as React.ComponentProps<'div'>)} />
    </>
  )
}

export const DesktopSidebar = ({
  className,
  children,
  ...props
}: React.ComponentProps<typeof motion.div>) => {
  const { open, animate } = useSidebar()
  return (
    <motion.div
      className={cn(
        'hidden md:flex md:flex-col bg-card w-[240px] flex-shrink-0 px-4 py-4 border-r border-border h-full',
        className
      )}
      animate={{
        width: animate ? (open ? '240px' : '80px') : '240px',
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

export const MobileSidebar = ({
  className,
  children,
  ...props
}: React.ComponentProps<'div'>) => {
  const { open, setOpen } = useSidebar()
  return (
    <>
      <div
        className={cn(
          'h-10 px-4 py-4 flex flex-row md:hidden items-center justify-between bg-card w-full border-b border-border'
        )}
        {...props}
      >
        <div className="flex justify-end z-20 w-full">
          <button
            onClick={() => setOpen(!open)}
            className="p-2 rounded-lg hover:bg-accent transition-colors"
          >
            <ChevronRight
              className={cn(
                'h-5 w-5 text-foreground transition-transform',
                open && 'rotate-90'
              )}
            />
          </button>
        </div>
        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ x: '-100%', opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: '-100%', opacity: 0 }}
              transition={{
                duration: 0.3,
                ease: 'easeInOut',
              }}
              className={cn(
                'fixed inset-0 bg-card h-full w-full z-[100] flex flex-col justify-between',
                className
              )}
            >
              <div
                className="absolute right-4 top-4 z-50 text-foreground"
                onClick={() => setOpen(!open)}
              >
                <ChevronRight className="h-5 w-5 rotate-90" />
              </div>
              {children}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  )
}

export const SidebarLink = ({
  link,
  className,
  ...props
}: {
  link: {
    label: string
    href: string
    icon: React.JSX.Element | React.ReactNode
  }
  className?: string
  props?: React.AnchorHTMLAttributes<HTMLAnchorElement>
}) => {
  const { open, animate } = useSidebar()
  return (
    <Link
      to={link.href}
      className={cn(
        'flex items-center gap-3 group/sidebar py-2.5 px-3 rounded-lg',
        'hover:bg-accent dark:hover:bg-neutral-800 transition-all duration-200',
        'text-foreground hover:text-primary',
        open ? 'justify-start' : 'justify-center',
        className
      )}
      {...props}
    >
      {link.icon}

      <motion.span
        animate={{
          display: animate ? (open ? 'inline-block' : 'none') : 'inline-block',
          opacity: animate ? (open ? 1 : 0) : 1,
        }}
        className="text-sm font-medium whitespace-pre truncate"
      >
        {link.label}
      </motion.span>
    </Link>
  )
}
