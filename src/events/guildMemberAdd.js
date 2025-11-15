const { Events } = require('discord.js');
const { getAutorole } = require('../database');

module.exports = {
    name: Events.GuildMemberAdd,
    async execute(member) {
        getAutorole(member.guild.id, async (roles) => {
            if (!roles) return;

            try {
                const roleId = member.user.bot ? roles.bot_role : roles.user_role;
                if (!roleId) return;

                const role = member.guild.roles.cache.get(roleId.toString());
                if (role) {
                    await member.roles.add(role);
                    console.log(`✅ Auto-role assigned to ${member.user.tag}`);
                }
            } catch (error) {
                console.error('Error assigning auto-role:', error);
            }
        });
    }
};
