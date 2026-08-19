
        function toggleDropdown(id) {
            document.getElementById(id).classList.toggle('active');
        }
        window.onclick = function(event) {
            if (!event.target.matches('.profile-circle')) {
                var dropdowns = document.getElementsByClassName("dropdown");
                for (var i = 0; i < dropdowns.length; i++) {
                    var openDropdown = dropdowns[i];
                    if (openDropdown.classList.contains('active')) {
                        openDropdown.classList.remove('active');
                    }
                }
            }
        }
        
        function toggleSidebar(forceState) {
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            if (!sidebar) return;
            
            if (typeof forceState === 'boolean') {
                if (forceState) {
                    sidebar.classList.add('active');
                    if (overlay) overlay.classList.add('active');
                    document.body.classList.add('drawer-open');
                } else {
                    sidebar.classList.remove('active');
                    if (overlay) overlay.classList.remove('active');
                    document.body.classList.remove('drawer-open');
                }
            } else {
                const isActive = sidebar.classList.toggle('active');
                if (overlay) overlay.classList.toggle('active', isActive);
                document.body.classList.toggle('drawer-open', isActive);
            }
        }

        // Anti-DevTools Deterrent
        document.addEventListener('keydown', event => {
            if (event.keyCode === 123 || (event.ctrlKey && event.shiftKey && (event.keyCode === 73 || event.keyCode === 74 || event.keyCode === 67)) || (event.ctrlKey && event.keyCode === 85)) {
                event.preventDefault();
                console.warn("Unauthorized access prohibited.");
            }
        });
    
